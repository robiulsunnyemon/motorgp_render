from pydantic import BaseModel,EmailStr


class UserBase(BaseModel):
    full_name: str


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserRead(UserBase):
    full_name: str
    email: EmailStr
    password: str
    is_verified: bool
    id: int


class ResendOTP(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    otp: int
    password: str


class UserOTPVerify(BaseModel):
    email: EmailStr
    otp:int

class LoginUserModel(BaseModel):
    email: EmailStr
    password: str