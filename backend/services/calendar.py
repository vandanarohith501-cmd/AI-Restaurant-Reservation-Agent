from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

def add_reservation_to_calendar(credentials_dict: dict, restaurant_name: str, date_str: str, time_str: str, address: str, phone: str):
    """
    Adds a reservation to the user's primary Google Calendar.
    `credentials_dict` should be the dictionary obtained from OAuth2 flow containing access_token, refresh_token, etc.
    """
    try:
        creds = Credentials(**credentials_dict)
        service = build('calendar', 'v3', credentials=creds)

        # Parse date and time. Assume local timezone for now.
        start_datetime = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + datetime.timedelta(hours=1, minutes=30) # Default 1.5 hour reservation

        event = {
            'summary': f'Reservation at {restaurant_name}',
            'location': address,
            'description': f'Reservation for {restaurant_name}.\\nPhone: {phone}\\n\\nAutomatically added by AI Restaurant Reservation Agent.',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'UTC', # Adjust timezone if necessary
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }

        event_result = service.events().insert(calendarId='primary', body=event).execute()
        return event_result.get('htmlLink')
    except Exception as e:
        print(f"Error adding to calendar: {e}")
        return None
