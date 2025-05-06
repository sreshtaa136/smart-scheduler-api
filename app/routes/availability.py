from fastapi import APIRouter, HTTPException, Query
from dateutil.parser import isoparse
from app.db import mongo
from app.utils import filter_conflicts

router = APIRouter(prefix="/availability")

@router.get("/{provider_id}")
async def get_availability(
  provider_id: str,
  start: str = Query(..., description="ISO timestamp"),
  end: str = Query(..., description="ISO timestamp")
):
  # validate dates
  try:
    dt_start = isoparse(start)
    dt_end   = isoparse(end)
  except ValueError:
    raise HTTPException(400, "Invalid ISO date format")
  
  # load all seeded availability for this provider in the window
  avail_docs = await mongo.availability.find({
    "provider_id": provider_id,
    "start": {"$gte": dt_start.isoformat()},
    "end":   {"$lte": dt_end.isoformat()}
  }, {"_id": 0}).to_list(None)

  # load existing confirmed bookings
  booked = await mongo.appointments.find({
    "provider_id": provider_id
  }, {"_id": 0}).to_list(None)

  # filter out any slots that overlap a booking
  free_slots = filter_conflicts(avail_docs, booked)

  return {"available": free_slots}
