import typing as t

from asgiref import typing as at
from channels import layers
from channels.generic import websocket


class UrlRoute(t.TypedDict):
    args: tuple[str | int, ...]
    kwargs: dict[str, str | int]


class ChannelsWebSocketScope(at.WebSocketScope):
    url_route: UrlRoute


class ChatMessage(t.TypedDict):
    type: t.Literal["chat.message"]
    message: str


class Message(t.TypedDict):
    message: str


class ChatConsumer(websocket.AsyncJsonWebsocketConsumer):
    channel_layer: layers.BaseChannelLayer

    async def connect(self) -> None:
        scope: ChannelsWebSocketScope = self.scope
        self.room_name = scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, content: Message) -> None:
        message: ChatMessage = {"type": "chat.message", "message": content["message"]}

        # Send message to room group
        await self.channel_layer.group_send(self.room_group_name, message)

    # Receive message from room group
    async def chat_message(self, event: ChatMessage) -> None:
        message: Message = {"message": event["message"]}

        # Send message to WebSocket
        await self.send_json(content=message)
