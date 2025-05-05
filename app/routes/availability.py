from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.calendar_client import fetch_google_availability

router = APIRouter(prefix="/availability")

@router.get("/{provider_id}")
async def get_availability(
  provider_id: str,
  start: str = Query(..., description="ISO timestamp"),
  end: str = Query(..., description="ISO timestamp")
):
  # validate dates
  try:
    dt_start = datetime.fromisoformat(start)
    dt_end = datetime.fromisoformat(end)
  except ValueError:
    raise HTTPException(400, "Invalid ISO date format")
  # fetch slots
  google_slots = await fetch_google_availability(provider_id, dt_start, dt_end)
  return {"google": google_slots}
