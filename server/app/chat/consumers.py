import json

from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self) -> None:
        self.accept()

    def disconnect(self, close_code: str) -> None:
        pass

    def receive(self, text_data: str) -> None:
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
