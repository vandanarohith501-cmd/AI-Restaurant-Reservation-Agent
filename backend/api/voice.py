import json
import base64
import asyncio
import websockets
from fastapi import APIRouter, WebSocket, Request, WebSocketDisconnect, Depends
from fastapi.responses import Response
import os
from sqlalchemy.orm import Session
import crud
from database import get_db

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("/twiml/{reservation_id}")
async def get_twiml(request: Request, reservation_id: int):
    """
    Twilio will call this endpoint when an outgoing or incoming call is initiated.
    It returns TwiML instructions telling Twilio to connect the call audio to our WebSocket.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-your-openai-key-here":
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>The live voice calling feature is currently disabled because the OpenAI API key is missing. Please use the text chat interface.</Say>
    <Hangup/>
</Response>"""
        return Response(content=twiml, media_type="text/xml")

    host = request.headers.get("host", "localhost:8000")
    # In production, ensure wss:// is used. For local dev with ngrok, host will be the ngrok url.
    # We replace http with wss, or https with wss depending on the host
    protocol = "wss" if "localhost" not in host else "ws"
    ws_url = f"{protocol}://{host}/api/voice/stream/{reservation_id}"
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{ws_url}" />
    </Connect>
</Response>"""
    return Response(content=twiml, media_type="text/xml")


@router.websocket("/stream/{reservation_id}")
async def websocket_endpoint(websocket: WebSocket, reservation_id: int, db: Session = Depends(crud.get_db)):
    """
    Handles the bidirectional audio stream between Twilio and OpenAI Realtime API.
    """
    await websocket.accept()
    
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set")
        await websocket.close()
        return

    openai_ws_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    
    try:
        # Connect to OpenAI Realtime API
        async with websockets.connect(
            openai_ws_url,
            extra_headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
        ) as openai_ws:
            
            # Configure OpenAI Session (Voice Persona: Echo, System Prompt for negotiation)
            session_update = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],
                    "voice": "echo",
                    "instructions": "You are a casual male assistant calling a restaurant to book a table on behalf of a user. Be polite and conversational. If the exact time requested is not available, you must politely end the call and say you need to check with the user, UNLESS they gave a time window. Once the reservation is either confirmed or denied, you MUST call the finalize_reservation tool.",
                    "input_audio_format": "g711_ulaw",
                    "output_audio_format": "g711_ulaw",
                    "tools": [
                        {
                            "type": "function",
                            "name": "finalize_reservation",
                            "description": "Call this when the reservation is successfully confirmed, or if it failed (e.g., no availability).",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "enum": ["confirmed", "failed"]}
                                },
                                "required": ["status"]
                            }
                        }
                    ]
                }
            }
            await openai_ws.send(json.dumps(session_update))

            stream_sid = None

            async def receive_from_twilio():
                nonlocal stream_sid
                try:
                    while True:
                        data = await websocket.receive_text()
                        message = json.loads(data)
                        
                        if message["event"] == "start":
                            stream_sid = message["start"]["streamSid"]
                            print(f"Started Twilio stream: {stream_sid}")
                            
                        elif message["event"] == "media":
                            # Send audio payload to OpenAI
                            audio_payload = message["media"]["payload"]
                            audio_event = {
                                "type": "input_audio_buffer.append",
                                "audio": audio_payload
                            }
                            await openai_ws.send(json.dumps(audio_event))
                            
                        elif message["event"] == "stop":
                            print("Twilio stream stopped.")
                            break
                except WebSocketDisconnect:
                    print("Twilio disconnected")
                except Exception as e:
                    print(f"Error receiving from Twilio: {e}")

            async def receive_from_openai():
                nonlocal stream_sid
                try:
                    while True:
                        data = await openai_ws.recv()
                        event = json.loads(data)
                        
                        if event["type"] == "response.audio.delta":
                            if stream_sid:
                                # Send AI audio payload back to Twilio
                                audio_payload = event["delta"]
                                media_message = {
                                    "event": "media",
                                    "streamSid": stream_sid,
                                    "media": {
                                        "payload": audio_payload
                                    }
                                }
                                await websocket.send_text(json.dumps(media_message))
                        
                        elif event["type"] == "response.function_call_arguments.done":
                            if event["name"] == "finalize_reservation":
                                try:
                                    args = json.loads(event["arguments"])
                                    status = args.get("status")
                                    if status in ["confirmed", "failed"]:
                                        print(f"Finalizing reservation {reservation_id} with status: {status}")
                                        crud.update_reservation_status(db, reservation_id, status)
                                        # Tell the model we processed it
                                        func_result = {
                                            "type": "conversation.item.create",
                                            "item": {
                                                "type": "function_call_output",
                                                "call_id": event["call_id"],
                                                "output": json.dumps({"success": True})
                                            }
                                        }
                                        await openai_ws.send(json.dumps(func_result))
                                except Exception as e:
                                    print(f"Error handling function call: {e}")
                                
                except websockets.exceptions.ConnectionClosed:
                    print("OpenAI disconnected")
                except Exception as e:
                    print(f"Error receiving from OpenAI: {e}")

            # Run both loops concurrently
            await asyncio.gather(
                receive_from_twilio(),
                receive_from_openai()
            )
    except Exception as e:
        print(f"Failed to connect to OpenAI Realtime: {e}")
        await websocket.close()
