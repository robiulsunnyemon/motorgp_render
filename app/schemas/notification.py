from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class NotificationBase(BaseModel):
    user_id: int
    race_id: int
    notification_hour: int

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    notification_hour: Optional[int] = None

class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
