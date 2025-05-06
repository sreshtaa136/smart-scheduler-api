from fastapi import APIRouter
from app.db import mongo
from app.utils import filter_conflicts
from app.llm_client import recommend_slots
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, List

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

class Slot(BaseModel):
  start: datetime
  end: datetime
  reason: str

class RecommendResponse(BaseModel):
  recommendations: List[Slot]


@router.post("/", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):  
  # gather availability & existing bookings
  availabilities = await mongo.availability.find({
    "provider_id": request.provider_id,
    "start": {"$gte": request.start.isoformat()},
    "end":   {"$lte": request.end.isoformat()}
  }, {"_id": 0}).to_list(None)

  booked = await mongo.appointments.find({
    "provider_id": request.provider_id
  }, {"_id": 0}).to_list(None)

  free_slots = filter_conflicts(availabilities, booked)

  # ask the LLM, get back a List[dict]
  suggestions = await recommend_slots(request.patient, free_slots)

  # return parsed suggestions directly
  return RecommendResponse(recommendations=suggestions)
