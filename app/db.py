import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

client = AsyncIOMotorClient(
  os.getenv("MONGO_URI"),
  tls=True,
  tlsCAFile=certifi.where()
)
mongo = client.scheduler_db
