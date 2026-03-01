from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import numpy as np
from app.database import get_db
from app.models.models import Availability, Booking

router = APIRouter()


class CarePathItem(BaseModel):
    party_id: int
    duration_slots: int


class FindOptimalSlotRequest(BaseModel):
    day_of_week: int
    care_path: List[CarePathItem]


def get_availability_matrix(party_ids: List[int], day: int, db: Session) -> np.ndarray:
    """
    Build a 2D matrix of availability for all parties.
    Returns: numpy array of shape (num_parties, 36)
    Rows are in order of party_ids list.
    """
    matrix = []
    
    for party_id in party_ids:
        avail = db.query(Availability).filter(
            Availability.party_id == party_id,
            Availability.day_of_week == day
        ).first()
        
        booking = db.query(Booking).filter(
            Booking.party_id == party_id,
            Booking.day_of_week == day
        ).first()
        
        avail_slots = avail.slots if avail else [0] * 36
        booking_slots = booking.slots if booking else [0] * 36
        
        # Combine: effective_blocked (OR logic)
        effective = [
            1 if avail_slots[i] == 1 or booking_slots[i] == 1 else 0
            for i in range(36)
        ]
        matrix.append(effective)
    
    return np.array(matrix)


def build_mask_matrix(care_path: List[CarePathItem], party_ids: List[int], total_slots: int) -> np.ndarray:
    """
    Build a 2D mask matrix for all parties.
    Returns: numpy array of shape (num_parties, total_slots)
    Rows are in order of party_ids list.
    Gap (party_id=0) just advances time without adding constraints.
    """
    # Create mapping: party_id -> row index
    party_to_row = {pid: idx for idx, pid in enumerate(party_ids)}
    
    # Initialize mask matrix with zeros
    mask_matrix = np.zeros((len(party_ids), total_slots), dtype=int)
    
    # Fill in the mask for each care path step
    current_pos = 0
    for item in care_path:
        if item.party_id == 0:  # Gap - just advance time, no constraint
            current_pos += item.duration_slots
            continue
        row = party_to_row[item.party_id]
        for i in range(item.duration_slots):
            mask_matrix[row, current_pos + i] = 1
        current_pos += item.duration_slots
    
    return mask_matrix



def check_conflict_at_position(availability_matrix: np.ndarray, 
                                mask_matrix: np.ndarray, 
                                start: int) -> bool:
    """
    Check if there's a conflict at the given start position.
    Adds availability window + mask, checks if any cell == 2.
    Returns: True if conflict, False if valid.
    """
    total_slots = mask_matrix.shape[1]
    
    # Slice the availability matrix for this window
    availability_window = availability_matrix[:, start:start + total_slots]
    
    # Add matrices: if any cell == 2, there's a conflict
    combined = availability_window + mask_matrix
    
    return 2 in combined


def build_schedule(care_path: List[CarePathItem], start: int) -> List[dict]:
    """
    Build the schedule output showing each party's time slots.
    """
    schedule = []
    current_pos = 0
    
    for item in care_path:
        schedule.append({
            "party_id": item.party_id,
            "start_slot": start + current_pos,
            "end_slot": start + current_pos + item.duration_slots - 1
        })
        current_pos += item.duration_slots
    
    return schedule


@router.post("/find-optimal-slot")
def find_optimal_slot(request: FindOptimalSlotRequest, db: Session = Depends(get_db)):
    """
    Find the first available continuous window for the care path.
    Uses 2D NumPy matrices for efficient conflict detection.
    """
    day = request.day_of_week
    care_path = request.care_path
    
    # Calculate total slots needed
    total_slots = sum(item.duration_slots for item in care_path)
    
    if total_slots > 36:
        return {"found": False, "message": "Care path too long for a single day"}
    
    # Get unique party IDs (preserve order), excluding gaps (party_id=0)
    party_ids = list(dict.fromkeys(item.party_id for item in care_path if item.party_id != 0))

    
    # Build 2D matrices
    availability_matrix = get_availability_matrix(party_ids, day, db)  # (num_parties, 36)

    mask_matrix = build_mask_matrix(care_path, party_ids, total_slots)  # (num_parties, total_slots)
    
    # Slide the window: try each starting position
    for start in range(36 - total_slots + 1):
        if not check_conflict_at_position(availability_matrix, mask_matrix, start):
            # Found a valid position!
            return {
                "found": True,
                "start_slot": start,
                "end_slot": start + total_slots - 1,
                "schedule": build_schedule(care_path, start)
            }
    
    return {"found": False, "message": "No available slot found for this day"}
