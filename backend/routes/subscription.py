from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime

from models.user import User
from models.subscription import SubscriptionTier
from utils.auth import get_current_user
from utils.payment import (
    create_payment, 
    verify_and_update_subscription, 
    approve_simulated_payment_and_update,
    is_subscription_active
)

# Pydantic models for requests and responses
from pydantic import BaseModel

class SubscriptionUpdate(BaseModel):
    tier_id: str

# Create router
router = APIRouter()

@router.get("/subscription-tiers")
async def get_subscription_tiers():
    """Get all available subscription tiers"""
    tiers = await SubscriptionTier.find_all().to_list()
    
    # Format the response
    tier_list = [
        {
            "id": tier.id,
            "name": tier.name,
            "price": tier.price,
            "course_limit": tier.course_limit,
            "description": tier.description
        }
        for tier in tiers
    ]
    
    return tier_list

@router.post("/subscribe")
async def subscribe(subscription: SubscriptionUpdate, current_user: User = Depends(get_current_user)):
    """Subscribe to a tier (direct update)"""
    # Make sure the tier exists
    tier = await SubscriptionTier.find_one(SubscriptionTier.id == subscription.tier_id)
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription tier not found"
        )
    
    # For free tier, update directly
    if tier.price == 0:
        # Update user subscription
        current_user.subscription_tier = tier.id
        # Free tier has no expiration
        current_user.subscription_expiration = None
        await current_user.save()
        
        return {
            "success": True,
            "subscription": {
                "tier": tier.name,
                "expiration": None
            }
        }
    else:
        # For paid tiers, redirect to payment
        return {
            "success": False,
            "message": "Please use the /create-payment endpoint for paid subscriptions"
        }

@router.get("/subscription-status")
async def get_subscription_status(current_user: User = Depends(get_current_user)):
    """Get the current user's subscription status"""
    # Get user's subscription tier
    tier_id = current_user.subscription_tier or "free"
    tier = await SubscriptionTier.find_one(SubscriptionTier.id == tier_id)
    
    if not tier:
        tier = await SubscriptionTier.find_one(SubscriptionTier.id == "free")
        if not tier:
            # Create a default free tier if it doesn't exist
            tier = SubscriptionTier(
                id="free",
                name="Free",
                price=0,
                course_limit=1,
                description="Access to 1 course only"
            )
            await tier.insert()
    
    # Check if subscription is active
    is_active = await is_subscription_active(current_user)
    
    # Calculate remaining time if applicable
    remaining_days = None
    if current_user.subscription_expiration and is_active:
        delta = current_user.subscription_expiration - datetime.utcnow()
        remaining_days = max(0, delta.days)
    
    return {
        "tier": {
            "id": tier.id,
            "name": tier.name,
            "price": tier.price,
            "course_limit": tier.course_limit,
            "description": tier.description
        },
        "is_active": is_active,
        "expiration": current_user.subscription_expiration.isoformat() if current_user.subscription_expiration else None,
        "remaining_days": remaining_days
    }

@router.post("/create-payment")
async def create_payment_route(subscription: SubscriptionUpdate, current_user: User = Depends(get_current_user)):
    """Create a payment for a subscription"""
    # Get the tier
    tier = await SubscriptionTier.find_one(SubscriptionTier.id == subscription.tier_id)
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription tier not found"
        )
    
    # For free tier, update directly
    if tier.price == 0:
        current_user.subscription_tier = tier.id
        current_user.subscription_expiration = None
        await current_user.save()
        
        return {
            "success": True,
            "message": "Subscribed to free tier successfully"
        }
    
    # For paid tiers, create a payment
    payment_result = await create_payment(current_user, tier.id)
    
    return payment_result

@router.post("/verify-payment")
async def verify_payment_route(payment_data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """Verify a payment and update subscription if successful"""
    # Make sure the payment reference is provided
    if "reference" not in payment_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment reference is required"
        )
    
    # Verify the payment and update subscription
    result = await verify_and_update_subscription(current_user, payment_data["reference"])
    
    return result

@router.post("/approve-simulated-payment")
async def approve_simulated_payment_route(payment_data: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """Approve a simulated payment (for testing purposes only)"""
    # Make sure the payment reference is provided
    if "reference" not in payment_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment reference is required"
        )
    
    # Approve the simulated payment and update subscription
    result = await approve_simulated_payment_and_update(current_user, payment_data["reference"])
    
    return result 