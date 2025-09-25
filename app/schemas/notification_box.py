from  pydantic import BaseModel


class NotificationBox(BaseModel):
    user_id :int
    notification_title: str
    notification_body: str