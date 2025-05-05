from datetime import datetime

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
