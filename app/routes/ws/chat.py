import json
import asyncio
from typing import List
from app.core.ws import ProtectedWebSocket, broadcaster
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

chat_routes = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@chat_routes.websocket("/")
async def main_chat(ws: WebSocket):
    # ws_session = ProtectedWebSocket(ws)
    # await ws_session.accept()
    await ws.accept()
    
    async def receive_loop():
        try:
            while True:
                data = await ws.receive_json()
                # validate incoming message
                if data.get("type") != "message" or not isinstance(data.get("message"), str):
                    raise WebSocketDisconnect
                await broadcaster.publish("chat", "data")
        except (ValueError, WebSocketDisconnect):
            raise WebSocketDisconnect

    async def send_loop():
        async with broadcaster.subscribe("chat") as subscriber:
            async for event in subscriber:
                try:
                    await ws.send_text(event.message)
                except WebSocketDisconnect:
                    break

    try:
        # Run both loops concurrently
        await asyncio.gather(receive_loop(), send_loop())
    except WebSocketDisconnect:
        await ws.close(1001)