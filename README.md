# Medical Scheduling System

A full-stack medical scheduling application that finds the optimal time slot for a patient's multi-step care path using a NumPy-powered 2D sliding window matrix algorithm. Built as a take-home assessment.

## Demo & Presentation

- **Video Walkthrough:** [YouTube — Solving Medical Scheduling with a Sliding Window Matrix Algorithm](YOUR_YOUTUBE_LINK_HERE)
- **Presentation Slides:** [Presentation.pptx](./Presentation.pptx)

## Overview

Healthcare scheduling requires coordinating multiple parties (Doctor, NMT, Patient, Scan) while avoiding conflicts and minimizing patient wait time. This system solves that by:

- Allowing staff to define a **care path** (e.g., Doctor → Gap → NMT → Scan)
- Automatically finding the **earliest contiguous window** where all required parties are available using a NumPy matrix algorithm
- Supporting **manual block/unblock** of slots and **persistent bookings** per party per day

## Tech Stack

| Layer    | Technology                                           |
| -------- | ---------------------------------------------------- |
| Backend  | Python, FastAPI, SQLAlchemy, SQLite, NumPy           |
| Frontend | Angular 18 (standalone components), TypeScript, SCSS |
| Auth     | JWT (python-jose), bcrypt password hashing           |

## Project Structure

```
backend/
  main.py                  # FastAPI app entry point
  app/
    database.py            # SQLAlchemy engine & session
    dependencies.py        # Auth dependency (JWT validation)
    init_db.py             # DB creation & seed data
    models/models.py       # Party, Availability, Booking, Appointment
    routes/
      auth.py              # Login & /me endpoints
      parties.py           # GET /parties
      availability.py      # GET/PUT availability per day
      scheduling.py        # POST /find-optimal-slot (NumPy algorithm)
      appointments.py      # POST /appointments (booking)
    services/
      auth_service.py      # Password hashing, JWT create/verify

frontend/
  src/app/
    pages/
      login/               # Login page
      scheduling/          # Main scheduling grid + care path builder
    services/
      api.service.ts       # HTTP calls to backend
      api.models.ts        # TypeScript interfaces
      auth.service.ts      # JWT storage & expiry checking
    interceptors/
      auth.interceptor.ts  # Attaches Bearer token, handles 401
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

### Backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The database (`scheduling.db`) is created automatically on first startup with seed data (4 parties, empty availability for all 7 days).

### Frontend

```bash
cd frontend
npm install
ng serve
```

The Angular dev server runs on **http://localhost:4200**.

## Default Credentials

| Username | Password  |
| -------- | --------- |
| admin    | admin123  |
| doctor   | doctor123 |

## API Endpoints

| Method | Endpoint              | Auth | Description                                      |
| ------ | --------------------- | ---- | ------------------------------------------------ |
| POST   | `/auth/login`         | No   | Returns JWT access token                         |
| GET    | `/auth/me`            | Yes  | Returns current user info                        |
| GET    | `/parties`            | No   | Lists all active parties                         |
| GET    | `/availability/{day}` | No   | Combined availability + bookings for a day (0–6) |
| PUT    | `/availability`       | Yes  | Block/unblock slots for a party on a day         |
| POST   | `/find-optimal-slot`  | No   | Finds earliest available window for a care path  |
| POST   | `/appointments`       | Yes  | Books an appointment and blocks slots            |

## Scheduling Algorithm

1. **Availability matrix** — 2D NumPy array (parties × 36 slots), where `1` = blocked/booked.
2. **Mask matrix** — 2D array encoding which party needs which relative time slots in the care path.
3. **Sliding window** — the mask slides across all 36 positions; at each position, availability + mask are added. If any cell equals `2`, there's a conflict.
4. The **first conflict-free position** is returned with the full schedule breakdown.

Gaps (`party_id = 0`) advance time without constraining any party — useful for wait times between steps.

## Time Slots

The day is divided into **36 slots** of 15 minutes each, covering **8:00 AM – 5:00 PM** (Monday through Sunday).

## Key Features

- **Availability grid** — visual table of time slots × parties, color-coded (green = free, grey = blocked, red = booked, gold = found slot)
- **Click/drag selection** — block or unblock slots by selecting and clicking Block/Unblock (requires login)
- **Care path builder** — compose multi-step care paths with optional gaps between parties
- **Optimal slot search** — one-click search highlights the best available window on the grid
- **Booking confirmation** — enter patient name, confirm, and slots are marked as booked for all involved parties
- **JWT auth** — token auto-attaches via interceptor, auto-redirects on expiry

## Design Assumptions

- **Patient availability** — patients are always available; blocked by default in the scheduling matrix
- **Fixed time slots** — 36 slots per day (8 AM–5 PM) with 15-minute granularity
- **Single-day scope** — scheduling operates within one calendar day at a time

## Future Enhancements

- Dynamic party management and role-based access control
- Patient information storage with notifications and reminders
- Multi-day scheduling and analytics dashboard
- Administration panel for managing parties and users
