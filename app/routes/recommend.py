from fastapi import APIRouter, HTTPException
from app.db import mongo
from app.calendar_client import fetch_google_availability
from app.utils import filter_conflicts
from app.llm_client import recommend_slots
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict

router = APIRouter(prefix="/recommend")

class PatientInfo(BaseModel):
  name: str
  preferences: Dict[str, bool] = Field(
    default_factory=dict,
    description="E.g. {'morning_only': True}"
  )
  conditions: str = Field(
    default_factory="",
    description="E.g. 'hypertension', 'diabetes', etc."
  )

# request body includes provider, window, and patient info
class RecommendRequest(BaseModel):
  provider_id: str
  start: datetime
  end: datetime
  patient: PatientInfo


@router.post("/")
async def recommend(request: dict):
  # lookup patient profile
  # patient = await mongo.patients.find_one({"_id": request["patient_id"]})
  # if not patient:
  #   raise HTTPException(404, "Patient not found")

  # fetch all potential slots
  dt_start = datetime.fromisoformat(request["start"])
  dt_end   = datetime.fromisoformat(request["end"])
  slots = await fetch_google_availability(request["provider_id"], dt_start, dt_end)
  # load existing appts and filter conflicts
  existing = await mongo.appointments.find({
    "provider_id": request["provider_id"]
  }).to_list(None)
  free_slots = filter_conflicts(slots, existing)
  # ask the LLM for up to 3 recommendations
  suggestion = await recommend_slots(request.patient.dict(), free_slots)
  return {"recommendations": suggestion}
