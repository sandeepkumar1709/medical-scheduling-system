from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.models import Appointment, Booking
from app.dependencies import get_current_user

router = APIRouter()


class ScheduleItem(BaseModel):
    party_id: int
    start_slot: int
    end_slot: int


class CreateAppointmentRequest(BaseModel):
    patient_name: str
    day_of_week: int
    start_slot: int
    end_slot: int
    care_path: List[dict]
    schedule: List[ScheduleItem]
    notes: Optional[str] = None
    created_by: Optional[str] = None


def create_appointment_record(request: CreateAppointmentRequest, db: Session) -> Appointment:
    """
    Create and save the Appointment record.
    Returns the created appointment.
    """
    appointment = Appointment(
        patient_name=request.patient_name,
        day_of_week=request.day_of_week,
        start_slot=request.start_slot,
        end_slot=request.end_slot,
        care_path=request.care_path,
        status="confirmed",
        notes=request.notes,
        created_by=request.created_by
    )
    db.add(appointment)
    db.flush()
    return appointment


def get_or_create_booking(party_id: int, day_of_week: int, db: Session) -> Booking:
    """
    Get existing booking row or create a new one.
    """
    booking = db.query(Booking).filter(
        Booking.party_id == party_id,
        Booking.day_of_week == day_of_week
    ).first()
    
    if not booking:
        booking = Booking(
            party_id=party_id,
            day_of_week=day_of_week,
            slots=[0] * 36,
            patient_names=[""] * 36
        )
        db.add(booking)
        db.flush()
    
    return booking


def block_slots_for_party(booking: Booking, start_slot: int, end_slot: int, patient_name: str):
    """
    Block slots and set patient name for a booking.
    """
    slots = booking.slots.copy()
    patient_names = booking.patient_names.copy()
    
    for slot_idx in range(start_slot, end_slot + 1):
        slots[slot_idx] = 1
        patient_names[slot_idx] = patient_name
    
    booking.slots = slots
    booking.patient_names = patient_names


def update_bookings_for_schedule(request: CreateAppointmentRequest, db: Session):
    """
    Update booking table for all parties in the schedule.
    """
    for item in request.schedule:
        booking = get_or_create_booking(item.party_id, request.day_of_week, db)
        block_slots_for_party(booking, item.start_slot, item.end_slot, request.patient_name)


@router.post("/appointments")
def create_appointment(request: CreateAppointmentRequest, 
                       db: Session = Depends(get_db),
                       current_user: str = Depends(get_current_user)):
    """
    Create a new appointment and block the slots in booking table.
    """
    # 1. Create Appointment record
    appointment = create_appointment_record(request, db)
    
    # 2. Update Booking table for each party
    update_bookings_for_schedule(request, db)
    
    # 3. Commit all changes
    db.commit()
    
    return {
        "message": "Appointment created successfully",
        "appointment_id": appointment.id
    }
