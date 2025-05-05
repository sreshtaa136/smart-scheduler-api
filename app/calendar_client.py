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

# checks the provider's calendar and returns all events in the given window
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
  body = {
    "summary": f"Appointment with patient {appointment['patient_id']}",
    "start": {"dateTime": appointment["start"]},
    "end": {"dateTime": appointment["end"]},
  }
  return service.events().insert(calendarId=calendar_id, body=body).execute()
