from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    google_id: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RestaurantBase(BaseModel):
    place_id: str
    name: str
    address: str
    phone_number: str
    rating: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantResponse(RestaurantBase):
    id: int
    
    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    reservation_time: datetime
    guest_count: int
    special_instructions: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    restaurant_id: int
    status: str
    created_at: datetime
    restaurant: RestaurantResponse
    
    class Config:
        from_attributes = True
