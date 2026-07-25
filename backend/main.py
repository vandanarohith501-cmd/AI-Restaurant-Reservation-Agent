from fastapi import FastAPI
from api import reservations, agent, voice, auth

app = FastAPI(title="AI Restaurant Reservation API")

app.include_router(reservations.router, prefix="/api", tags=["reservations"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Restaurant Reservation API"}
