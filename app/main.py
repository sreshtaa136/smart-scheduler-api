import os
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.calendar_client import book_google_event
from app.routes import availability, recommend, booking
from contextlib import asynccontextmanager
from app.db import mongo

load_dotenv()

# --- Sample data -------------------------------------------------------------

AEST = ZoneInfo("Australia/Melbourne")
sample_providers = [
  {"id": "sreshtaaias@gmail.com", "name": "Dr. Alice Smith", "specialties": ["cardiology"]},
  {"id": "sreshtaa.t@gmail.com", "name": "Dr. Bob Jones",   "specialties": ["dermatology","general"]},
]

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

# ------------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
  # --- STARTUP: seed data once ---
  # providers
  if await mongo.providers.count_documents({}) == 0:
    await mongo.providers.insert_many(sample_providers)

  # appointments with rollback on failure
  if await mongo.appointments.count_documents({}) == 0:
    for appt in sample_appointments:
      inserted_id = None
      try:
        result = await mongo.appointments.insert_one(appt)
        inserted_id = result.inserted_id
        await book_google_event(appt["provider_id"], appt)
      except Exception as e:
        if inserted_id:
            await mongo.appointments.delete_one({"_id": inserted_id})
        print(f"⚠️ Rolled back seed for {appt['provider_id']}: {e}")

  # yield control to FastAPI so it starts serving
  yield

app = FastAPI(
  title="Smart Scheduler",
  lifespan=lifespan
)
app.include_router(availability.router)
app.include_router(recommend.router)
app.include_router(booking.router)
