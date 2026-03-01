from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Party

router = APIRouter()


@router.get("/parties")
def get_parties(db: Session = Depends(get_db)):
    """Get all active parties."""
    parties = db.query(Party).filter(Party.is_active == True).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "color": p.color
        }
        for p in parties
    ]
