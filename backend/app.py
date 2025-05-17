from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import database connection
from db import init_db

# Import route modules
from routes import auth, courses, subscription

# Import document models
from models.user import User
from models.course import Course
from models.subscription import SubscriptionTier

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(title="Course Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from modules
app.include_router(auth.router, tags=["Authentication"])
app.include_router(courses.router, tags=["Courses"])
app.include_router(subscription.router, tags=["Subscription"])

# Startup event to initialize database
@app.on_event("startup")
async def startup_db_client():
    try:
        await init_db()
        print("Database connection established")
        
        # Initialize subscription tiers if they don't exist
        await initialize_subscription_tiers()
    except Exception as e:
        print(f"Failed to connect to database: {str(e)}")

async def initialize_subscription_tiers():
    """Initialize default subscription tiers if they don't exist"""
    # Check if any tiers exist
    count = await SubscriptionTier.find().count()
    
    if count == 0:
        # Create default tiers
        tiers = [
            SubscriptionTier(
                id="tier_free",
                name="Free",
                price=0,
                course_limit=1,
                description="Access to 1 course only"
            ),
            SubscriptionTier(
                id="tier_pro",
                name="Pro",
                price=19.90,
                course_limit=5,
                description="Ideal para usuarios regulares"
            ),
            SubscriptionTier(
                id="tier_unlimited",
                name="Unlimited",
                price=24.90,
                course_limit=-1,
                description="Perfecto para uso intensivo"
            )
        ]
        
        # Insert all tiers
        for tier in tiers:
            await tier.insert()
            
        print(f"Initialized {len(tiers)} default subscription tiers")

@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {"message": "Course Generator API is running"}

# For direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 