from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import crud, models, schemas
from database import get_db
from services.places import get_restaurant_details

router = APIRouter()

@router.get("/user/{user_id}/reservations", response_model=List[schemas.ReservationResponse])
def read_user_reservations(user_id: int, db: Session = Depends(get_db)):
    reservations = crud.get_user_reservations(db, user_id=user_id)
    return reservations

@router.post("/reservations", response_model=schemas.ReservationResponse)
def create_reservation(reservation: schemas.ReservationCreate, user_id: int, place_id: str, db: Session = Depends(get_db)):
    # In a real scenario, user_id comes from auth token
    # First, get or create restaurant
    db_restaurant = crud.get_restaurant_by_place_id(db, place_id=place_id)
    if not db_restaurant:
        place_data = get_restaurant_details(place_id)
        if not place_data:
            raise HTTPException(status_code=404, detail="Restaurant not found in mock data")
        
        rest_create = schemas.RestaurantCreate(
            place_id=place_id,
            name=place_data["name"],
            address=place_data["address"],
            phone_number=place_data["phone_number"],
            rating=place_data["rating"]
        )
        db_restaurant = crud.create_restaurant(db, restaurant=rest_create)
    
    return crud.create_reservation(db=db, reservation=reservation, user_id=user_id, restaurant_id=db_restaurant.id)

from services.calendar import add_reservation_to_calendar
from services.notifications import send_whatsapp_confirmation

class SyncRequest(BaseModel):
    google_credentials: dict
    user_phone: str

@router.post("/{reservation_id}/sync")
def sync_reservation(reservation_id: int, request: SyncRequest, db: Session = Depends(get_db)):
    """
    Syncs a confirmed reservation to Google Calendar and sends an SMS/WhatsApp confirmation.
    """
    db_reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not db_reservation or db_reservation.status != "confirmed":
        raise HTTPException(status_code=400, detail="Reservation not found or not confirmed yet.")
    
    restaurant = db_reservation.restaurant
    date_str = db_reservation.reservation_time.strftime("%Y-%m-%d")
    time_str = db_reservation.reservation_time.strftime("%H:%M")
    
    # Add to Calendar
    calendar_link = add_reservation_to_calendar(
        credentials_dict=request.google_credentials,
        restaurant_name=restaurant.name,
        date_str=date_str,
        time_str=time_str,
        address=restaurant.address,
        phone=restaurant.phone_number
    )
    
    # Send SMS/WhatsApp
    sms_sent = send_whatsapp_confirmation(
        to_number=request.user_phone,
        restaurant_name=restaurant.name,
        date=date_str,
        time=time_str
    )
    
    return {
        "success": True,
        "calendar_link": calendar_link,
        "sms_sent": sms_sent
    }
