from channels.generic.websocket import AsyncWebsocketConsumer

class PokerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        await self.close()

    async def receive(self, text_data):
        # Handle incoming messages from the WebSocket
        await self.send(text_data=text_data)