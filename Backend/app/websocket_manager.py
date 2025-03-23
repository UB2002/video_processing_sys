# app/websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect

class WebSocketManager:
    """Handles WebSocket connections."""
    
    def __init__(self):
        self.clients = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accepts WebSocket connection and stores client."""
        await websocket.accept()
        self.clients[client_id] = websocket
    
    async def disconnect(self, client_id: str):
        """Removes disconnected clients."""
        if client_id in self.clients:
            del self.clients[client_id]
    
    async def send_message(self, client_id: str, message: dict):
        """Sends a JSON message to a specific client."""
        if client_id in self.clients:
            await self.clients[client_id].send_json(message)

ws_manager = WebSocketManager()
