from beanie import Document
from datetime import datetime
from typing import Dict
from uuid import uuid4


class Course(Document):
    id: str = str(uuid4())
    user_id: str  # referenciando ID del usuario
    title: str
    prompt: str
    content: Dict  # JSON-like content
    experience_level: str
    available_time: str
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = 'courses'
