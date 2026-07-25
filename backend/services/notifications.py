import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") # Default Twilio sandbox

def send_whatsapp_confirmation(to_number: str, restaurant_name: str, date: str, time: str):
    """
    Sends a WhatsApp confirmation using Twilio Sandbox.
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("Twilio credentials not found. Skipping WhatsApp notification.")
        return False
        
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Ensure numbers are formatted correctly for WhatsApp
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
            
        message_body = f"✅ Your reservation at *{restaurant_name}* for {date} at {time} has been successfully confirmed!"
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )
        print(f"WhatsApp message sent! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
        return False
