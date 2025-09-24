from fastapi import APIRouter, Depends, HTTPException,status
from app.schemas.user import UserCreate, UserRead, UserOTPVerify, ResendOTP, ResetPassword, LoginUserModel
from app.db.db import get_db
from app.models.user import UserModel
from sqlalchemy.orm import Session
from app.utils.get_hashed_password import get_hashed_password,verify_password
from typing import List
from app.utils.email_config import send_otp
from app.utils.otp_generate import generate_otp
from app.schemas.send_otp import SendOtpModel
from app.utils.token_generation import create_access_token
from fastapi.security import OAuth2PasswordRequestForm




router = APIRouter(prefix="/user", tags=["User"])



@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(user:UserCreate,db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You have already registered")
    hashed_password = get_hashed_password(user.password)
    otp=generate_otp()
    send_otp_data=SendOtpModel(email=user.email,otp=otp)
    await send_otp(send_otp_data)
    new_user = UserModel(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
        otp=otp,
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"A 6 digit OTP has delivered. please check your email"}



@router.post("/user_otp_verify", status_code=status.HTTP_200_OK)
async def verify_otp(user:UserOTPVerify,db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if user.otp != db_user.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Wrong OTP")
    db_user.is_verified = True
    db.commit()
    db.refresh(db_user)
    return {"message":"You have  verified"}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user:LoginUserModel,db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Wrong password")

    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You are not verified, please check your email")

    token=create_access_token(data={"sub": db_user.email,"user_id":db_user.id})
    return {"access_token":token,"token_type":"bearer"}



# @router.post("/login", status_code=status.HTTP_200_OK)
#
# async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     db_user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
#     if db_user is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#
#     if not verify_password(form_data.password, db_user.password):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")
#
#     if not db_user.is_verified:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not verified, please check your email")
#
#     token = create_access_token(data={"sub": db_user.email, "role": db_user.role, "user_id": db_user.id})
#     return {"access_token": token, "token_type": "bearer"}




@router.post("/resend-otp", status_code=status.HTTP_200_OK)
async def resend_otp(user:ResendOTP,db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    otp=generate_otp()
    send_otp_data = SendOtpModel(email=user.email, otp=otp)
    await send_otp(send_otp_data)
    db_user.otp=otp
    db.commit()
    db.refresh(db_user)
    return {"message":"A 6 digit OTP has delivered. please check your email"}


@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(user:ResetPassword,db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if db_user.otp != user.otp :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Wrong OTP")
    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You are not verified")
    db_user.otp = user.otp
    hashed_password = get_hashed_password(user.password)
    db_user.password = hashed_password
    db.commit()
    db.refresh(db_user)
    return {"message":"you have reset password successfully"}


@router.get("/all_user",response_model= List[UserRead] ,status_code=status.HTTP_200_OK)
async def read_users(db: Session = Depends(get_db)):
    db_users = db.query(UserModel).all()
    return db_users

@router.get("/{id}",response_model=UserRead ,status_code=status.HTTP_200_OK)
async def read_user_by_id(id: int,db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == id).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return db_user


@router.delete("/{id}",status_code=status.HTTP_200_OK)
async def delete_user(id:int,db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == id).first()
    if db_user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message":"user deleted successfully"}