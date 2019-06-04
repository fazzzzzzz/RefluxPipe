import json

from channels.generic.websocket import AsyncWebsocketConsumer


class updateResult(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.username = self.scope["session"]["username"]
            self.group_name = 'group_%s' % self.username
        except:
            return 0
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except:
            pass

    async def client_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
