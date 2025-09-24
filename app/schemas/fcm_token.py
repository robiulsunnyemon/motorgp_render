from pydantic import BaseModel

class FCMToken(BaseModel):
    user_id:int
    token: str