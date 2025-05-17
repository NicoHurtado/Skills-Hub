from beanie import Document
from pydantic import EmailStr
from datetime import datetime
from typing import Optional
from uuid import uuid4


class User(Document):
    id: str = str(uuid4())
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime = datetime.utcnow()
    subscription_tier: Optional[str] = None
    subscription_expiration: Optional[datetime] = None

    class Settings:
        name = 'users'
