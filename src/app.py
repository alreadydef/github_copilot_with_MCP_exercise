"""High School Management System API.

A simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

class SessionCreate(BaseModel):
    date: str = Field(..., description="Session date in YYYY-MM-DD format")
    start_time: str = Field(..., description="Start time in HH:MM (24-hour) format")
    end_time: str = Field(..., description="End time in HH:MM (24-hour) format")
    location: Optional[str] = Field(default=None, description="Optional session location")


class SessionUpdate(BaseModel):
    date: Optional[str] = Field(default=None, description="Session date in YYYY-MM-DD format")
    start_time: Optional[str] = Field(default=None, description="Start time in HH:MM (24-hour) format")
    end_time: Optional[str] = Field(default=None, description="End time in HH:MM (24-hour) format")
    location: Optional[str] = Field(default=None, description="Optional session location")


session_id_counter = 1


def _validate_date(date_str: str) -> None:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="date must be in YYYY-MM-DD format") from exc


def _validate_time(time_str: str) -> None:
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="time must be in HH:MM format") from exc


def _validate_session_window(date_str: str, start_time: str, end_time: str) -> None:
    _validate_date(date_str)
    _validate_time(start_time)
    _validate_time(end_time)

    start_dt = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date_str} {end_time}", "%Y-%m-%d %H:%M")
    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="end_time must be later than start_time")


def _create_session(date_str: str, start_time: str, end_time: str, location: Optional[str] = None) -> dict:
    global session_id_counter
    _validate_session_window(date_str, start_time, end_time)

    session = {
        "id": session_id_counter,
        "date": date_str,
        "start_time": start_time,
        "end_time": end_time,
        "location": location,
    }
    session_id_counter += 1
    return session


def _session_start(session: dict) -> datetime:
    return datetime.strptime(f"{session['date']} {session['start_time']}", "%Y-%m-%d %H:%M")


def _sorted_sessions(sessions: list[dict]) -> list[dict]:
    return sorted(sessions, key=_session_start)


def _upcoming_sessions(sessions: list[dict]) -> list[dict]:
    now = datetime.now()
    return [session for session in _sorted_sessions(sessions) if _session_start(session) >= now]


def _get_activity_or_404(activity_name: str) -> dict:
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "sessions": [
            _create_session("2026-03-27", "15:30", "17:00", "Room 201"),
            _create_session("2026-04-03", "15:30", "17:00", "Room 201"),
        ],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "sessions": [
            _create_session("2026-03-24", "15:30", "16:30", "Lab A"),
            _create_session("2026-03-26", "15:30", "16:30", "Lab A"),
        ],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "sessions": [
            _create_session("2026-03-23", "14:00", "15:00", "Main Gym"),
            _create_session("2026-03-25", "14:00", "15:00", "Main Gym"),
        ],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "sessions": [
            _create_session("2026-03-24", "16:00", "17:30", "Soccer Field"),
            _create_session("2026-03-26", "16:00", "17:30", "Soccer Field"),
        ],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "sessions": [
            _create_session("2026-03-25", "15:30", "17:00", "West Court"),
            _create_session("2026-03-27", "15:30", "17:00", "West Court"),
        ],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "sessions": [
            _create_session("2026-03-26", "15:30", "17:00", "Art Studio"),
            _create_session("2026-04-02", "15:30", "17:00", "Art Studio"),
        ],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "sessions": [
            _create_session("2026-03-23", "16:00", "17:30", "Auditorium"),
            _create_session("2026-03-25", "16:00", "17:30", "Auditorium"),
        ],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "sessions": [
            _create_session("2026-03-24", "15:30", "16:30", "Room 105"),
            _create_session("2026-03-31", "15:30", "16:30", "Room 105"),
        ],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "sessions": [
            _create_session("2026-03-27", "16:00", "17:30", "Debate Hall"),
            _create_session("2026-04-03", "16:00", "17:30", "Debate Hall"),
        ],
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return {
        name: {
            **details,
            "sessions": _sorted_sessions(details.get("sessions", [])),
            "upcoming_sessions": _upcoming_sessions(details.get("sessions", [])),
        }
        for name, details in activities.items()
    }


@app.get("/activities/{activity_name}/sessions")
def get_activity_sessions(activity_name: str):
    """Get all scheduled sessions for an activity."""
    activity = _get_activity_or_404(activity_name)
    return {
        "activity": activity_name,
        "sessions": _sorted_sessions(activity.get("sessions", [])),
    }


@app.post("/advisor/activities/{activity_name}/sessions")
def create_activity_session(activity_name: str, session: SessionCreate):
    """Advisor endpoint for creating a new scheduled session."""
    activity = _get_activity_or_404(activity_name)
    new_session = _create_session(
        session.date,
        session.start_time,
        session.end_time,
        session.location,
    )
    activity.setdefault("sessions", []).append(new_session)
    return {
        "message": f"Created session for {activity_name}",
        "session": new_session,
    }


@app.put("/advisor/activities/{activity_name}/sessions/{session_id}")
def update_activity_session(activity_name: str, session_id: int, session_update: SessionUpdate):
    """Advisor endpoint for updating an existing scheduled session."""
    activity = _get_activity_or_404(activity_name)
    sessions = activity.get("sessions", [])

    for session in sessions:
        if session["id"] != session_id:
            continue

        if session_update.date is not None:
            _validate_date(session_update.date)
            session["date"] = session_update.date
        if session_update.start_time is not None:
            _validate_time(session_update.start_time)
            session["start_time"] = session_update.start_time
        if session_update.end_time is not None:
            _validate_time(session_update.end_time)
            session["end_time"] = session_update.end_time
        if session_update.location is not None:
            session["location"] = session_update.location

        _validate_session_window(session["date"], session["start_time"], session["end_time"])

        return {
            "message": f"Updated session {session_id} for {activity_name}",
            "session": session,
        }

    raise HTTPException(status_code=404, detail="Session not found")


@app.delete("/advisor/activities/{activity_name}/sessions/{session_id}")
def delete_activity_session(activity_name: str, session_id: int):
    """Advisor endpoint for deleting a scheduled session."""
    activity = _get_activity_or_404(activity_name)
    sessions = activity.get("sessions", [])

    for index, session in enumerate(sessions):
        if session["id"] == session_id:
            removed_session = sessions.pop(index)
            return {
                "message": f"Deleted session {session_id} from {activity_name}",
                "session": removed_session,
            }

    raise HTTPException(status_code=404, detail="Session not found")


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activity = _get_activity_or_404(activity_name)

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    activity = _get_activity_or_404(activity_name)

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
