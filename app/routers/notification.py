from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.db import get_db
from app.models.notification import NotificationModel
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationUpdate

notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])


# Get all notifications
@notification_router.get("/", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db)):
    return db.query(NotificationModel).all()


# Get notification by id
@notification_router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


# Create notification
@notification_router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    db_notification = NotificationModel(**notification.model_dump())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


# Update notification
@notification_router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(notification_id: int, updated_data: NotificationUpdate, db: Session = Depends(get_db)):
    notification = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(notification, key, value)

    db.commit()
    db.refresh(notification)
    return notification


# Delete notification
@notification_router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return
