from typing import Dict, Any, List, Callable
from fastapi import WebSocket
import json
import asyncio
from abc import ABC, abstractmethod

class WebSocketConnection:
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscriptions: List[str] = []

class WebSocketEventHandler(ABC):
    @abstractmethod
    async def handle_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class AttendanceEventHandler(WebSocketEventHandler):
    async def handle_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement actual event handling logic
        print(f"Processing attendance event: {event_type} with data: {data}")
        return {"status": "processed", "event": event_type}

class WebSocketManager:
    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._event_handlers: Dict[str, WebSocketEventHandler] = {}
        self._event_subscribers: Dict[str, List[str]] = {}

    def register_handler(self, event_type: str, handler: WebSocketEventHandler):
        """Register an event handler for a specific event type"""
        self._event_handlers[event_type] = handler

    async def connect(self, websocket: WebSocket, client_id: str):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self._connections[client_id] = WebSocketConnection(websocket, client_id)
        await self.broadcast_system_message(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self._connections:
            # Remove client subscriptions
            for event_type in list(self._event_subscribers.keys()):
                if client_id in self._event_subscribers[event_type]:
                    self._event_subscribers[event_type].remove(client_id)
            del self._connections[client_id]

    async def subscribe(self, client_id: str, event_types: List[str]):
        """Subscribe client to specific event types"""
        if client_id not in self._connections:
            return

        for event_type in event_types:
            if event_type not in self._event_subscribers:
                self._event_subscribers[event_type] = []
            if client_id not in self._event_subscribers[event_type]:
                self._event_subscribers[event_type].append(client_id)
                self._connections[client_id].subscriptions.append(event_type)

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast event to subscribed clients"""
        if event_type not in self._event_subscribers:
            return

        # Process event with registered handler
        handler = self._event_handlers.get(event_type)
        if handler:
            processed_data = await handler.handle_event(event_type, data)
        else:
            processed_data = data

        # Broadcast to subscribers
        for client_id in self._event_subscribers[event_type]:
            if client_id in self._connections:
                try:
                    await self._connections[client_id].websocket.send_json({
                        "type": event_type,
                        "data": processed_data
                    })
                except Exception as e:
                    print(f"Error sending to client {client_id}: {e}")
                    # TODO: Implement proper error handling and logging

    async def broadcast_system_message(self, message: str):
        """Broadcast system message to all connected clients"""
        for connection in self._connections.values():
            try:
                await connection.websocket.send_json({
                    "type": "system",
                    "message": message
                })
            except Exception as e:
                print(f"Error sending system message to {connection.client_id}: {e}")
                # TODO: Implement proper error handling and logging

# Global WebSocket manager instance
ws_manager = WebSocketManager() 