from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import messaging
from sqlalchemy.orm import Session
from typing import List
from app.db.db import get_db
from app.models.notification import NotificationModel
from app.models.promotions import PromotionModel
from app.schemas.promotions import PromotionCreate, PromotionResponse, PromotionUpdate
from app.models.fcm_token import FCMTokenModel


promotion_router = APIRouter(prefix="/promotions", tags=["Promotions"])


# Get all promotions
@promotion_router.get("/", response_model=List[PromotionResponse])
def get_promotions(db: Session = Depends(get_db)):
    return db.query(PromotionModel).all()


# Get promotion by id
@promotion_router.get("/{promotion_id}", response_model=PromotionResponse)
def get_promotion(promotion_id: int, db: Session = Depends(get_db)):
    promotion = db.query(PromotionModel).filter(PromotionModel.id == promotion_id).first()
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")
    return promotion


# Create promotion
@promotion_router.post("/", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
def create_promotion(promotion: PromotionCreate, db: Session = Depends(get_db)):

    db_promotion = PromotionModel(**promotion.model_dump())
    db.add(db_promotion)
    db.commit()
    db.refresh(db_promotion)

    db_tokens = db.query(FCMTokenModel).all()
    tokens = [token.token for token in db_tokens]

    if not tokens:
        print("No FCM tokens found. Promotion created but no notifications sent.")
        return db_promotion

    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=promotion.title,
                body=promotion.description,  # ✅ এখানে description ব্যবহার করো
            ),
            tokens=tokens,
        )

        response = messaging.send_each_for_multicast(message)
        print(f'{response.success_count} messages were sent successfully')
        for token_obj in db_tokens:
            notification = NotificationModel(
                user_id=token_obj.user_id,
                title=promotion.title,
                message=promotion.description,
            )
            db.add(notification)
        db.commit()


    except Exception as e:
        print(f"Failed to send push notifications: {e}")

    return db_promotion









# Update promotion
@promotion_router.put("/{promotion_id}", response_model=PromotionResponse)
def update_promotion(promotion_id: int, updated_data: PromotionUpdate, db: Session = Depends(get_db)):
    promotion = db.query(PromotionModel).filter(PromotionModel.id == promotion_id).first()
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")

    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(promotion, key, value)

    db.commit()
    db.refresh(promotion)
    return promotion


# Delete promotion
@promotion_router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promotion(promotion_id: int, db: Session = Depends(get_db)):
    promotion = db.query(PromotionModel).filter(PromotionModel.id == promotion_id).first()
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")

    db.delete(promotion)
    db.commit()
    return
