from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    reservations = relationship("Reservation", back_populates="user")

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String, unique=True, index=True)  # Google Places ID
    name = Column(String, index=True)
    address = Column(String)
    phone_number = Column(String)
    rating = Column(String, nullable=True)
    
    reservations = relationship("Reservation", back_populates="restaurant")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    reservation_time = Column(DateTime)
    guest_count = Column(Integer)
    status = Column(String, default="pending")  # pending, confirmed, cancelled, failed
    special_instructions = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reservations")
    restaurant = relationship("Restaurant", back_populates="reservations")
    logs = relationship("CallLog", back_populates="reservation")

class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"))
    call_sid = Column(String, unique=True, index=True)  # Twilio Call SID
    status = Column(String)
    duration = Column(Integer, nullable=True)  # in seconds
    recording_url = Column(String, nullable=True)
    transcript = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reservation = relationship("Reservation", back_populates="logs")
