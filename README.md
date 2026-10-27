# AI Restaurant Reservation Agent 🤖🍽️

A production-ready, full-stack AI agent capable of booking restaurant tables via natural language chat and **real-time voice phone calls**. It integrates with Google Places, OpenAI Realtime API, Twilio, and Google Calendar.

## 🌟 Features
- **AI Chat & Voice Booking**: Users can chat or use the microphone to book tables.
- **Real-Time Voice Calls**: The backend uses Twilio WebSockets to stream audio to OpenAI's Realtime API, acting as a human assistant calling the restaurant.
- **Google Calendar Sync**: Automatically adds the confirmed reservation to your Google Calendar.
- **WhatsApp/SMS Confirmations**: Sends a receipt of the booking to the user's phone via Twilio.
- **Glassmorphism UI**: A premium, dark-mode React interface.

---

## 🏗️ Architecture Stack
- **Frontend**: React.js, Vite, Vanilla CSS (Glassmorphism), Google OAuth.
- **Backend**: Python, FastAPI, SQLAlchemy (SQLite/PostgreSQL).
- **AI Agent Engine**: LangGraph, LangChain, OpenAI GPT-4o.
- **Telephony API**: Twilio WebSockets + OpenAI Realtime API.
- **Deployment**: Docker & Docker Compose.

---

## 🚀 Quick Start (Docker)

The fastest way to run the entire stack locally is using Docker Compose.

### 1. Prerequisites
- [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/) installed.
- API Keys ready (OpenAI, Twilio).

### 2. Environment Variables
Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your_openai_key_here
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
GOOGLE_CLIENT_SECRETS_FILE=client_secrets.json
```
*(Ensure you download your `client_secrets.json` from Google Cloud Console and place it in the `backend/` folder).*

### 3. Spin up the Stack
Run the following command in the root folder:
```bash
docker-compose up --build -d
```

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **Database**: PostgreSQL on port 5432

---

## 💻 Manual Setup (Local Development)

If you prefer to run the components separately for development:

### Backend
# Navigate to the backend folder
cd backend

# Activate the Python virtual environment
.\venv\Scripts\activate

# Create your .env file (if you haven't already)
Copy-Item .env.example .env

# Run the backend server
uvicorn main:app --reload
```

### Frontend
# Navigate to the frontend folder
cd frontend

# Install the Node.js dependencies (only needed the first time)
npm install

# Start the development server
npm run dev

---

## 🧪 Testing

End-to-end UI testing is configured using **Cypress**.

1. Start your frontend server (`npm run dev`).
2. Run Cypress:
```bash
cd frontend
npx cypress open
```

---

## 📄 License
MIT License.
