from datetime import datetime, timedelta, date, timezone
from zoneinfo import ZoneInfo
import calendar
import uuid

AEST = ZoneInfo("Australia/Melbourne")

# returns True if slot overlaps any existing appointment.
def is_conflict(slot: dict, existing: list[dict]) -> bool:
  # takes an ISO-formatted date/time string
  # & parses it into a datetime.datetime object
  start_new = datetime.fromisoformat(slot["start"])
  end_new = datetime.fromisoformat(slot["end"])

  for appointment in existing:
    start_existing = datetime.fromisoformat(appointment["start"])
    end_existing = datetime.fromisoformat(appointment["end"])
    # if not (slot ends before or starts after the appointment)
    # then its an overlap
    if not (end_new <= start_existing or start_new >= end_existing):
      return True
  return False

# remove any slots that clash with existing appointments
def filter_conflicts(slots: list[dict], existing: list[dict]) -> list[dict]:
  result = []
  for slot in slots:
    # keep this slot only if it does NOT conflict with any in existing
    if not is_conflict(slot, existing):
      result.append(slot)
  return result

def generate_ics(appointment: dict) -> str:
  """
  Build a minimal .ics file content for the given appointment dict.
  """
  # Ensure we have UTC datetimes for DTSTART/DTEND
  dtstart = appointment["start"]
  dtend   = appointment["end"]
  if isinstance(dtstart, str):
    # parse ISO back to datetime with tzinfo
    dtstart = datetime.fromisoformat(dtstart)
  if isinstance(dtend, str):
    dtend = datetime.fromisoformat(dtend)

  # Convert to UTC for ICS standard
  dtstart_utc = dtstart.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
  dtend_utc   = dtend.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
  dtstamp     = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
  uid         = appointment.get("_id", uuid.uuid4())

  summary = "Doctor's Appointment"
  description = appointment.get("notes", "")

  ics = "\r\n".join([
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Intelligent Scheduler//EN",
    "BEGIN:VEVENT",
    f"UID:{uid}",
    f"DTSTAMP:{dtstamp}",
    f"DTSTART:{dtstart_utc}",
    f"DTEND:{dtend_utc}",
    f"SUMMARY:{summary}",
    f"DESCRIPTION:{description}",
    "END:VEVENT",
    "END:VCALENDAR",
    ""
  ])
  return ics

def generate_monthly_slots(sample_providers: list[dict]):
  """Generate half-hour slots 09:00–12:00 and 13:00–17:00 on each weekday from tomorrow to month-end."""
  slots = []
  today_aest = datetime.now(AEST).date()
  year, month = today_aest.year, today_aest.month
  last_day = calendar.monthrange(year, month)[1]
  # slot hours: mornings 9–11, afternoons 13–16
  hours = list(range(9, 12)) + list(range(13, 17))
  for day in range(today_aest.day + 1, last_day + 1):
    current = date(year, month, day)
    # skip weekends
    if current.weekday() >= 5:
      continue
    for hour in hours:
      for minute in (0, 30):
        start_dt = datetime(year, month, day, hour, minute, tzinfo=AEST)
        end_dt   = start_dt + timedelta(minutes=30)
        iso_start = start_dt.isoformat()
        iso_end   = end_dt.isoformat()
        for prov in sample_providers:
          slots.append({
            "provider_id": prov["id"],
            "start": iso_start,
            "end":   iso_end
          })
  return slots