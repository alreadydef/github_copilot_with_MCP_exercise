# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View upcoming scheduled sessions for each activity
- Advisor session management via API (create, edit, delete)

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/activities/{activity_name}/sessions`                            | Get all scheduled sessions for an activity                          |
| POST   | `/advisor/activities/{activity_name}/sessions`                    | Create a new scheduled session for an activity                      |
| PUT    | `/advisor/activities/{activity_name}/sessions/{session_id}`       | Update an existing scheduled session                                |
| DELETE | `/advisor/activities/{activity_name}/sessions/{session_id}`       | Delete a scheduled session                                          |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule (legacy free-text field)
   - Structured sessions list with:
     - Session id
     - Date (`YYYY-MM-DD`)
     - Start time (`HH:MM`)
     - End time (`HH:MM`)
     - Optional location
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
