import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import availability, recommend, booking
from contextlib import asynccontextmanager
from app.db import mongo
from app.sample_data import sample_providers
from app.utils import generate_monthly_slots

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
  # --- STARTUP: seed data once ---
  # providers
  if await mongo.providers.count_documents({}) == 0:
    await mongo.providers.insert_many(sample_providers)

  # seed availability slots throughout the month
  monthly_slots = generate_monthly_slots(sample_providers)
  if await mongo.availability.count_documents({}) == 0:
    for slot in monthly_slots:
      inserted_id = None
      try:
        # insert into Mongo
        res = await mongo.availability.insert_one(slot)
        inserted_id = res.inserted_id
        # create transparent “Available” event on Google
        # await create_availability_event(slot["provider_id"], slot)
      except Exception as e:
        # # rollback on failure
        # if inserted_id:
        #   await mongo.availability.delete_one({"_id": inserted_id})
        print(f"⚠️ Rolled back availability for {slot['provider_id']} at {slot['start']}: {e}")

  # appointments with rollback on failure
  # if await mongo.appointments.count_documents({}) == 0:
  #   for appt in sample_appointments:
  #     inserted_id = None
  #     try:
  #       result = await mongo.appointments.insert_one(appt)
  #       inserted_id = result.inserted_id
  #       await book_google_event(appt["provider_id"], appt)
  #     except Exception as e:
  #       if inserted_id:
  #           await mongo.appointments.delete_one({"_id": inserted_id})
  #       print(f"⚠️ Rolled back seed for {appt['provider_id']}: {e}")

  # yield control to FastAPI so it starts serving
  yield

app = FastAPI(
  title="Smart Scheduler",
  lifespan=lifespan
)
app.include_router(availability.router)
app.include_router(recommend.router)
app.include_router(booking.router)
