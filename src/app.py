"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from typing import List

from sqlmodel import Session, select

from .db import init_db, get_session
from .models import Activity, Participant, SQLModel


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")


INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


def seed_db_if_empty(session: Session):
    """Seed the database with initial activities if none exist."""
    statement = select(Activity)
    results = session.exec(statement).all()
    if results:
        return

    for name, data in INITIAL_ACTIVITIES.items():
        activity = Activity(name=name,
                            description=data["description"],
                            schedule=data["schedule"],
                            max_participants=data["max_participants"])
        session.add(activity)
        session.commit()
        # add participants
        for email in data.get("participants", []):
            participant = Participant(email=email, activity_name=name)
            session.add(participant)
        session.commit()


@app.on_event("startup")
def on_startup():
    init_db()
    # seed if empty
    for s in get_session():
        seed_db_if_empty(s)
        break


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(session: Session = Depends(get_session)):
    statement = select(Activity)
    activities = session.exec(statement).all()
    out = {}
    for act in activities:
        part_stmt = select(Participant).where(Participant.activity_name == act.name)
        parts = [p.email for p in session.exec(part_stmt).all()]
        out[act.name] = {
            "description": act.description,
            "schedule": act.schedule,
            "max_participants": act.max_participants,
            "participants": parts,
        }
    return out


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, session: Session = Depends(get_session)):
    """Sign up a student for an activity"""
    activity = session.get(Activity, activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    part_stmt = select(Participant).where(Participant.activity_name == activity_name)
    participants = session.exec(part_stmt).all()

    if any(p.email == email for p in participants):
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(participants) >= activity.max_participants:
        raise HTTPException(status_code=400, detail="Activity is full")

    participant = Participant(email=email, activity_name=activity_name)
    session.add(participant)
    session.commit()
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, session: Session = Depends(get_session)):
    """Unregister a student from an activity"""
    activity = session.get(Activity, activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    part_stmt = select(Participant).where(Participant.activity_name == activity_name, Participant.email == email)
    participant = session.exec(part_stmt).first()
    if not participant:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    session.delete(participant)
    session.commit()
    return {"message": f"Unregistered {email} from {activity_name}"}
