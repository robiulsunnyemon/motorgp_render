from fastapi import APIRouter, Depends, HTTPException,status
from app.schemas.user import UserCreate
from app.db.db import get_db
from app.models.user import UserModel
from sqlalchemy.orm import Session
from app.utils.token_generation import create_access_token
from app.utils.user_info import get_user_info
from app.models.fcm_token import FCMTokenModel
router = APIRouter(prefix="/user", tags=["User"])



@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(user:UserCreate,db: Session = Depends(get_db)):
    new_user = UserModel(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db_fcm_token_user=db.query(FCMTokenModel).filter(FCMTokenModel.token==new_user.fcmToken).first()
    if db_fcm_token_user is None:
        new_token = FCMTokenModel(
            user_id=new_user.id,
            token=user.fcmToken
        )
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
    token = create_access_token(data={"sub": new_user.uid, "fcmToken": new_user.fcmToken})
    return {"access_token": token, "token_type": "bearer"}




@router.delete("/delete",status_code=status.HTTP_200_OK)
async def delete_user(db: Session = Depends(get_db),user: dict = Depends(get_user_info)):
    user_id=user["id"]
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message":"user deleted successfully"}