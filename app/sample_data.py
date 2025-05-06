from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sample_providers = [
  {"id": "sreshtaaias@gmail.com", "name": "Dr. Alice Smith", "specialties": ["cardiology"]},
  {"id": "sreshtaa.t@gmail.com", "name": "Dr. Bob Jones",   "specialties": ["dermatology","general"]},
]

AEST = ZoneInfo("Australia/Melbourne")
now_aest = datetime.now(AEST)
tomorrow = (now_aest + timedelta(days=1)).replace(hour=9,  minute=0, second=0, microsecond=0)
day_after = (now_aest + timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)

sample_appointments = [
  {
    "provider_id": "sreshtaaias@gmail.com",
    "start": tomorrow.isoformat(),
    "end": (tomorrow + timedelta(minutes=30)).isoformat(),
    "notes": "Initial consultation",
    "patient": {
      "name": "John Doe",
      "preferences": {"morning_only": True},
      "conditions": "hypertension",
    },
  },
  {
    "provider_id": "sreshtaa.t@gmail.com",
    "start": day_after.isoformat(),
    "end":   (day_after + timedelta(minutes=30)).isoformat(),
    "notes": "Skin rash follow-up",
    "patient": {
      "name": "Jane Roe",
      "preferences": {},
      "conditions": "eczema",
    },
  },
]

sample_availability = [
  {
    "provider_id": "sreshtaaias@gmail.com",
    "start": (tomorrow + timedelta(hours=1)).isoformat(),   # tomorrow @10:00
    "end":   (tomorrow + timedelta(hours=3)).isoformat(),   # tomorrow @12:00
  },
  {
    "provider_id": "sreshtaa.t@gmail.com",
    "start": (day_after.replace(hour=9, minute=0)).isoformat(),
    "end":   (day_after.replace(hour=11, minute=0)).isoformat(),
  },
]