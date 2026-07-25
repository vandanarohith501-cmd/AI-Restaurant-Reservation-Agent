import os
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session
import crud
from database import get_db

router = APIRouter()

# Client secrets file should be downloaded from Google Cloud Console
# For this project, we mock or load it from an env var/file.
CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "client_secrets.json")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.events"
]
# In production, redirect_uri would be https://domain.com/api/auth/callback
REDIRECT_URI = "http://localhost:8000/api/auth/callback"

@router.get("/login")
def login():
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return RedirectResponse(authorization_url)
    except FileNotFoundError:
        # Fallback if no secrets file for local dev
        return {"error": "Google Client Secrets file not found. Please set up OAuth in Google Cloud."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def auth_callback(request: Request, state: str, code: str, db: Session = Depends(get_db)):
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state, redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(authorization_response=str(request.url))
        
        credentials = flow.credentials
        session = flow.authorized_session()
        user_info = session.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
        
        # Save or update user in database
        user = crud.get_user_by_google_id(db, user_info['id'])
        if not user:
            from schemas import UserCreate
            user_create = UserCreate(
                email=user_info['email'],
                name=user_info['name'],
                google_id=user_info['id']
            )
            user = crud.create_user(db, user_create)
            
        # In a real app, you'd save credentials to the DB (securely encrypted) or create an app session token (JWT)
        # For simplicity, returning a token dict for frontend to hold in local storage
        creds_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        return {
            "message": "Login successful",
            "user": {"id": user.id, "email": user.email, "name": user.name},
            "credentials": creds_dict
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")
