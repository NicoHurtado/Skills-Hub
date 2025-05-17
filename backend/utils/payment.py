import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from models.user import User
from models.course import Course
from models.subscription import SubscriptionTier

# Import the payment service
try:
    from payment_service import create_payment_link, verify_payment, approve_simulated_payment, SIMULATION_MODE
    PAYMENT_ENABLED = True
except ImportError:
    # If the payment service module is not available, disable payment functionality
    PAYMENT_ENABLED = False
    print("WARNING: Payment service not available")

async def get_subscription_tier(tier_id: str) -> Optional[SubscriptionTier]:
    """Get a subscription tier by its ID"""
    return await SubscriptionTier.find_one(SubscriptionTier.id == tier_id)

async def is_subscription_active(user: User) -> bool:
    """Check if the user's subscription is still active"""
    if not user.subscription_tier or user.subscription_tier == "free":
        return True  # Free tier is always active
    
    if not user.subscription_expiration:
        return False
    
    return user.subscription_expiration > datetime.utcnow()

async def get_remaining_courses(user: User) -> int:
    """Get the number of courses remaining for the user"""
    if not user.subscription_tier:
        return 1  # Default to free tier
    
    # Get subscription details
    tier = await get_subscription_tier(user.subscription_tier)
    if not tier:
        return 1  # Default to free tier
    
    # Check for unlimited courses
    if tier.course_limit < 0:
        return -1  # Unlimited
    
    # Count how many courses the user has created
    courses_count = await Course.find(Course.user_id == user.id).count()
    remaining = max(0, tier.course_limit - courses_count)
    
    return remaining

async def create_payment(user: User, tier_id: str) -> Dict[str, Any]:
    """Create a payment for a subscription"""
    if not PAYMENT_ENABLED:
        return {"success": False, "error": "Payment service is not available"}
    
    # Get subscription details
    tier = await get_subscription_tier(tier_id)
    if not tier:
        return {"success": False, "error": "Invalid subscription tier"}
    
    # Create payment
    payment_result = create_payment_link(
        user_id=user.id,
        plan_id=tier.id,
        plan_name=tier.name,
        amount=tier.price
    )
    
    return payment_result

async def verify_and_update_subscription(user: User, reference: str) -> Dict[str, Any]:
    """Verify a payment and update the user's subscription"""
    if not PAYMENT_ENABLED:
        return {"success": False, "error": "Payment service is not available"}
    
    # Verify payment
    payment_result = verify_payment(reference)
    
    if payment_result["success"] and payment_result["status"] == "APPROVED":
        # Extract tier ID from reference
        parts = reference.split("_")
        if len(parts) >= 3:
            tier_id = parts[1]
            
            # Get subscription details
            tier = await get_subscription_tier(tier_id)
            if tier:
                # Update user subscription
                user.subscription_tier = tier_id
                user.subscription_expiration = datetime.utcnow() + timedelta(days=30)
                await user.save()
                
                return {
                    "success": True,
                    "subscription": {
                        "tier": tier.name,
                        "expiration": user.subscription_expiration.isoformat()
                    }
                }
    
    return payment_result

async def approve_simulated_payment_and_update(user: User, reference: str) -> Dict[str, Any]:
    """
    Approve a simulated payment and update the user's subscription
    Only for testing/simulation purposes
    """
    if not PAYMENT_ENABLED or not SIMULATION_MODE:
        return {"success": False, "error": "This function is only available in simulation mode"}
    
    # Approve payment
    payment_result = approve_simulated_payment(reference)
    
    if payment_result["success"]:
        # Extract tier ID from reference
        parts = reference.split("_")
        if len(parts) >= 3:
            tier_id = parts[1]
            
            # Get subscription details
            tier = await get_subscription_tier(tier_id)
            if tier:
                # Update user subscription
                user.subscription_tier = tier_id
                user.subscription_expiration = datetime.utcnow() + timedelta(days=30)
                await user.save()
                
                return {
                    "success": True,
                    "subscription": {
                        "tier": tier.name,
                        "expiration": user.subscription_expiration.isoformat()
                    }
                }
    
    return payment_result 