from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
from app.db import mongo
from app.calendar_client import book_google_event
from pydantic import EmailStr
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.utils_mail import send_appointment_email

router = APIRouter(prefix="/book")

class PatientInfo(BaseModel):
  name: str
  email: EmailStr
  preferences: Dict[str, bool] = Field(
    default_factory=dict,
    description="E.g. {'morning_only': True}"
  )
  conditions: str = Field(
    default_factory="",
    description="E.g. 'hypertension', 'diabetes', etc."
  )

class BookingRequest(BaseModel):
  provider_id: str
  start: datetime
  end: datetime
  notes: Optional[str] = Field(
    default="",
    description="Optional notes or reason for the appointment"
  )
  patient: PatientInfo

class BookingResponse(BaseModel):
  appointment_id: str
  event_link: Optional[str] = Field(
    None,
    description="URL to the booked Google Calendar event"
  )

@router.post("/", response_model=BookingResponse)
async def book(appointment: BookingRequest, background_tasks: BackgroundTasks):
  appt_data = appointment.model_dump()
  # get the provider's details
  provider = await mongo.providers.find_one({
    "id": appt_data["provider_id"]
  })
  if not provider:
    raise HTTPException(404, "Provider not found")
  appt_data["provider_name"] = provider["name"]
  res = await mongo.appointments.insert_one(appt_data)

  try:
    # create Google Calendar event
    event = await book_google_event(
      appt_data['provider_id'],
      appt_data
    )
  except Exception as e:
    # roll back if calendar booking fails
    await mongo.appointments.delete_one({"_id": res.inserted_id})
    raise HTTPException(
      status_code=502,
      detail=f"Failed to book on Google Calendar: {e}"
    )

  # remove that slot from our availability collection
  await mongo.availability.delete_one({
    "provider_id": appt_data["provider_id"],
    "start": appt_data["start"].isoformat(),
    "end": appt_data["end"].isoformat()
  })

  # schedule the email send in the background
  background_tasks.add_task(
    send_appointment_email,
    appointment.patient.email,
    appt_data,
  )

  # remove the “Available slot” event from the provider’s calendar
  # try:
    # await delete_availability_event(
    #   appt_data["provider_id"],
    #   {"start": appt_data["start"].isoformat(), "end": appt_data["end"].isoformat()}
    # )
  # except Exception as e:
  #   # log but do not rollback the booking
  #   print(f"⚠️ Failed to delete availability event: {e}")

  # return to client
  return BookingResponse(
    appointment_id=str(res.inserted_id),
    event_link=event.get("htmlLink")
  )
