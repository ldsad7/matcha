import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import Http404

from matcha.models import User, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        first_username, second_username = self.room_name.split('_')
        try:
            user_1 = User.objects_.filter(username=first_username)[0]
        except Exception:
            raise Http404(f"Пользователя с данным username ({first_username}) не существует в базе")
        try:
            user_2 = User.objects_.filter(username=second_username)[0]
        except Exception:
            raise Http404(f"Пользователя с данным username ({second_username}) не существует в базе")
        if user_1.username < user_2.username:
            self.user_1_id, self.user_2_id = user_1.id, user_2.id
            self.type = Message.TO_1_2
        else:
            self.user_1_id, self.user_2_id = user_2.id, user_1.id
            self.type = Message.TO_2_1

        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Leave room group
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
        Message(
            user_1_id=self.user_1_id,
            user_2_id=self.user_2_id,
            message=message,
            type=self.type
        ).save()

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
