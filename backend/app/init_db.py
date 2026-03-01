from app.database import engine, SessionLocal, Base
from app.models.models import Party, Availability, Booking


def init_database():
    """Create tables and seed default data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if parties already exist
        existing = db.query(Party).first()
        if existing:
            return  # Already initialized

        # Seed the 4 default parties
        default_parties = [
            Party(id=1, name="Doctor", color="#E07A5F"),
            Party(id=2, name="NMT", color="#3D85C6"),
            Party(id=3, name="Patient", color="#81B29A"),
            Party(id=4, name="Scan", color="#F4A261"),
        ]
        db.add_all(default_parties)

        # Initialize availability and bookings for all parties × 7 days
        empty_slots = [0] * 36
        empty_names = [""] * 36

        for party_id in [1, 2, 3, 4]:
            for day in range(7):
                # Patient (id=3) should have all slots blocked by default
                availability_slots = [1] * 36 if party_id == 3 else empty_slots
                db.add(Availability(party_id=party_id, day_of_week=day, slots=availability_slots))
                db.add(Booking(party_id=party_id, day_of_week=day, slots=empty_slots, patient_names=empty_names))


        db.commit()
    finally:
        db.close()
