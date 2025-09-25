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
async def registration(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter_by(uid=user.uid).first()

    if db_user is None:
        # নতুন ইউজার তৈরি
        new_user = UserModel(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # fcm token handle
        db_fcm_token_user = db.query(FCMTokenModel).filter(
            FCMTokenModel.token == new_user.fcmToken
        ).first()
        if db_fcm_token_user is None and new_user.fcmToken:
            new_token = FCMTokenModel(
                user_id=new_user.id,
                token=new_user.fcmToken
            )
            db.add(new_token)
            db.commit()
            db.refresh(new_token)

        uid = new_user.uid
        fcm_token = new_user.fcmToken
        status_code_return = status.HTTP_201_CREATED
    else:
        # পুরাতন ইউজার
        uid = db_user.uid
        fcm_token = db_user.fcmToken
        status_code_return = status.HTTP_200_OK

    token = create_access_token(data={"sub": uid, "fcmToken": fcm_token})
    return {
        "access_token": token,
        "token_type": "bearer",
        "status": status_code_return
    }





@router.delete("/delete",status_code=status.HTTP_200_OK)
async def delete_user(db: Session = Depends(get_db),user: dict = Depends(get_user_info)):
    user_id=user["id"]
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message":"user deleted successfully"}