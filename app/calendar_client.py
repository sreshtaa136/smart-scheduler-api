import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = [
  "https://www.googleapis.com/auth/calendar.readonly",  # fetch existing events
  "https://www.googleapis.com/auth/calendar.events",    # create/update events
]

# load service account credentials
creds = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), scopes=SCOPES
)
service = build("calendar", "v3", credentials=creds)

# checks the provider's calendar and returns all available slots in the given window
# calendar_id : provider's calendar email or id
# time_min, time_max : window to check availability
async def fetch_google_availability(calendar_id: str, time_min: datetime, time_max: datetime):
  # retrieve events in the given window
  events = service.events().list(
    calendarId=calendar_id,
    timeMin=time_min.isoformat(),
    timeMax=time_max.isoformat(),
    singleEvents=True,
    orderBy="startTime",
  ).execute()

  # returning a list of dictionaries
  return [
    {
      "provider_id": calendar_id,
      "start": ev["start"]["dateTime"],
      "end": ev["end"]["dateTime"],
    }
    for ev in events.get("items", [])
  ]

# creates a new calendar event for the booked appointment in the given calendar id
async def book_google_event(calendar_id: str, appointment: dict):
  """
  Expects appointment to include:
    - 'patient': dict with field 'name'
    - 'start', 'end': datetime objects (or ISO strings)
    - 'notes': optional string description
  """
  # Ensure start/end are ISO-formatted strings
  start_val = appointment["start"]
  end_val = appointment["end"]
  start_iso = start_val.isoformat() if isinstance(start_val, datetime) else start_val
  end_iso = end_val.isoformat() if isinstance(end_val, datetime) else end_val

  body = {
    "summary": f"Appointment with {appointment['patient']['name']}",
    "description": appointment.get("notes", ""),
    "start": {"dateTime": start_iso},
    "end": {"dateTime": end_iso},
  }

  # insert the event and return the created event object (includes 'htmlLink')
  event = service.events().insert(calendarId=calendar_id, body=body).execute()
  return event

async def create_availability_event(calendar_id: str, slot: dict):
  """
  Creates an 'Available' event on the provider's calendar.
  Use transparency='transparent' so it's treated as free time.
  """
  body = {
    "summary": "Available slot",
    "start": {"dateTime": slot["start"]},
    "end": {"dateTime": slot["end"]},
    "transparency": "transparent",
  }
  return service.events().insert(calendarId=calendar_id, body=body).execute()

async def delete_availability_event(calendar_id: str, slot: dict):
  """
  Finds any 'Available slot' events in the given window and removes them.
  """
  events = service.events().list(
    calendarId=calendar_id,
    timeMin=slot["start"],
    timeMax=slot["end"],
    singleEvents=True
  ).execute().get("items", [])

  for ev in events:
    if ev.get("summary") == "Available slot":
      service.events().delete(
        calendarId=calendar_id,
        eventId=ev["id"]
      ).execute()

