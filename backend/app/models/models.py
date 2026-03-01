from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class Party(Base):
    """
    Stores the parties (Doctor, NMT, Patient, Scan).
    Can be extended in future for CRUD operations.
    """
    __tablename__ = "parties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=False)  # Hex color like #E07A5F
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Availability(Base):
    """
    Stores manual availability blocks for each party per day.
    slots: JSON array of 36 integers (0=free, 1=blocked)
    """
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer, ForeignKey("parties.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    slots = Column(JSON, nullable=False)  # Array of 36 integers


class Booking(Base):
    """
    Stores booked appointment slots for each party per day.
    slots: JSON array of 36 integers (0=free, 1=booked)
    patient_names: JSON array of 36 strings (for tooltip on hover)
    """
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer, ForeignKey("parties.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    slots = Column(JSON, nullable=False)  # Array of 36 integers
    patient_names = Column(JSON, nullable=False)  # Array of 36 strings
    patient_ids = Column(JSON, nullable=True)  # Array of 36 integers for future patients table


class Appointment(Base):
    """
    Stores metadata for each booking.
    care_path: JSON array like [{"party_id": 1, "slots": 3}, ...]
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=True)  # For future patients table
    patient_name = Column(String(100), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_slot = Column(Integer, nullable=False)  # Starting slot index
    end_slot = Column(Integer, nullable=False)  # Ending slot index
    care_path = Column(JSON, nullable=False)  # The sequence used
    status = Column(String(20), default="confirmed")  # confirmed/cancelled/completed
    notes = Column(String(500), nullable=True)
    created_by = Column(String(100), nullable=True)  # For future multi-user
    created_at = Column(DateTime, server_default=func.now())
