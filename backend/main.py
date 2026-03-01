from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.init_db import init_database
from app.routes.parties import router as parties_router
from app.routes.availability import router as availability_router
from app.routes.scheduling import router as scheduling_router
from app.routes.appointments import router as appointments_router
from app.routes.auth import router as auth_router


app = FastAPI(title="Medical Scheduling API")

# Allow Angular frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parties_router)
app.include_router(availability_router)
app.include_router(scheduling_router)
app.include_router(appointments_router)
app.include_router(auth_router)

@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_database()


@app.get("/")
def root():
    return {"message": "Medical Scheduling API is running"}
