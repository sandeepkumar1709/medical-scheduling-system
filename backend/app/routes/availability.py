from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Availability, Booking, Party
from pydantic import BaseModel
from typing import List
from app.dependencies import get_current_user

router = APIRouter()

class UpdateAvailabilityRequest(BaseModel):
    party_id: int
    day_of_week: int
    slots: List[int]  # Array of 36 integers (0 or 1)

@router.put("/availability")
def update_availability(request: UpdateAvailabilityRequest, 
                        db: Session = Depends(get_db),
                        current_user: str = Depends(get_current_user)):
    """
    Update manual availability blocks for a party on a given day.
    Only updates the availability table, not bookings.
    """
    avail = db.query(Availability).filter(
        Availability.party_id == request.party_id,
        Availability.day_of_week == request.day_of_week
    ).first()
    
    if avail:
        avail.slots = request.slots
    else:
        avail = Availability(
            party_id=request.party_id,
            day_of_week=request.day_of_week,
            slots=request.slots
        )
        db.add(avail)
    
    db.commit()
    return {"message": "Availability updated successfully"}

@router.get("/availability/{day}")
def get_availability(day: int, db: Session = Depends(get_db)):
    """
    Get availability for all parties for a given day.
    day: 0=Monday, 1=Tuesday, ..., 6=Sunday
    
    Returns combined view: manual blocks + bookings = effective blocked slots
    """
    parties = db.query(Party).filter(Party.is_active == True).all()
    
    result = []
    for party in parties:
        # Get manual availability blocks
        avail = db.query(Availability).filter(
            Availability.party_id == party.id,
            Availability.day_of_week == day
        ).first()
        
        # Get bookings
        booking = db.query(Booking).filter(
            Booking.party_id == party.id,
            Booking.day_of_week == day
        ).first()
        
        avail_slots = avail.slots if avail else [0] * 36
        booking_slots = booking.slots if booking else [0] * 36
        patient_names = booking.patient_names if booking else [""] * 36
        
        # Combine: effective_blocked = availability OR bookings
        effective_blocked = [
            1 if avail_slots[i] == 1 or booking_slots[i] == 1 else 0
            for i in range(36)
        ]
        
        result.append({
            "party_id": party.id,
            "party_name": party.name,
            "party_color": party.color,
            "availability_slots": avail_slots,  # Manual blocks only
            "booking_slots": booking_slots,      # Bookings only
            "effective_blocked": effective_blocked,  # Combined
            "patient_names": patient_names
        })
    
    return result
