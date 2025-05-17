import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from models.user import User
from models.course import Course
from models.subscription import SubscriptionTier

load_dotenv()

async def init_db():
    # Get MongoDB connection details from environment variables
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    
    if not mongo_uri or not db_name:
        raise ValueError("MONGO_URI and DB_NAME must be set in .env file")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_uri)
    
    # Initialize Beanie with the document models
    await init_beanie(
        database=client[db_name],
        document_models=[User, Course, SubscriptionTier]
    )
    
    print(f"Connected to MongoDB database: {db_name}")
