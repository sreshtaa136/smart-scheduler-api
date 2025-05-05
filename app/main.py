import os
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Smart Scheduler")
mongo = AsyncIOMotorClient(os.getenv("MONGO_URI")).scheduler_db

from app.routes import availability, recommend, booking
app.include_router(availability.router)
app.include_router(recommend.router)
app.include_router(booking.router)
