from fastapi import FastAPI, Depends, HTTPException, APIRouter,status
from app.db.db import get_db
from sqlalchemy.orm import Session
from app.models.fcm_token import FCMTokenModel
from app.schemas.fcm_token import FCMToken
from typing import List

from app.utils.user_info import get_user_info

fcm_token_router = APIRouter(prefix="/fcm_token", tags=["FCM Token"])

@fcm_token_router.post('/', response_model=FCMToken, status_code=status.HTTP_201_CREATED)
async def create_token(token: FCMToken, db: Session = Depends(get_db),user: dict = Depends(get_user_info)):
    user_id = user["user_id"]
    new_token = FCMTokenModel(
        user_id=user_id,
        token=token.token
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token


@fcm_token_router.get('/', response_model=List[FCMToken], status_code=status.HTTP_200_OK)
async def get_tokens(db: Session = Depends(get_db)):
    tokens = db.query(FCMTokenModel).all()
    return tokens