from sqlalchemy import Column, String, Integer,Boolean,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.db import Base


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String,index=True,unique=True)
    email = Column(String,index=True,unique=True)
    password = Column(String)
    is_verified = Column(Boolean)
    otp = Column(Integer)
    create_time = Column(DateTime,server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())