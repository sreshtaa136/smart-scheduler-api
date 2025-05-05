from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict

class Provider(BaseModel):
  id: str
  name: str
  specialties: List[str]

class PatientProfile(BaseModel):
  id: str
  name: str
  preferences: Dict[str, bool]
  conditions: List[str]

class AvailabilitySlot(BaseModel):
  provider_id: str
  start: datetime
  end: datetime

class Appointment(BaseModel):
  id: str = Field(..., alias="_id")
  patient_id: str
  provider_id: str
  start: datetime
  end: datetime
  notes: str = ""
