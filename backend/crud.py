from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_user_by_google_id(db: Session, google_id: str):
    return db.query(models.User).filter(models.User.google_id == google_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, name=user.name, google_id=user.google_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_restaurant_by_place_id(db: Session, place_id: str):
    return db.query(models.Restaurant).filter(models.Restaurant.place_id == place_id).first()

def create_restaurant(db: Session, restaurant: schemas.RestaurantCreate):
    db_restaurant = models.Restaurant(**restaurant.model_dump())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def create_reservation(db: Session, reservation: schemas.ReservationCreate, user_id: int, restaurant_id: int):
    db_reservation = models.Reservation(
        user_id=user_id,
        restaurant_id=restaurant_id,
        reservation_time=reservation.reservation_time,
        guest_count=reservation.guest_count,
        special_instructions=reservation.special_instructions,
        status="pending"
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def update_reservation_status(db: Session, reservation_id: int, status: str):
    db_reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if db_reservation:
        db_reservation.status = status
        db.commit()
        db.refresh(db_reservation)
    return db_reservation

def get_user_reservations(db: Session, user_id: int):
    return db.query(models.Reservation).filter(models.Reservation.user_id == user_id).all()
