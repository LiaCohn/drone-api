from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
import os

uri = os.getenv("DB_URI")
name = os.getenv("DB_NAME")

# MongoDB connection
client = AsyncIOMotorClient(uri)

db = client.get_database(name)

# Drones Collection
drones_collection = db["Drones"]

# Missions Collection
missions_collection = db["Missions"]

# Schedules Collection
schedules_collection = db["Schedules"]

# Trajectories Collection
trajectories_collection = db["Trajectories"]
