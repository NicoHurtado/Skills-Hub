from beanie import Document
from typing import Optional


class SubscriptionTier(Document):
    id: str  # e.g., "basic", "premium"
    name: str
    price: float
    course_limit: int
    description: Optional[str]

    class Settings:
        name = 'subscription_tiers'
