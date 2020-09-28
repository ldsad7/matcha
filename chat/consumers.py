import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import Http404

from matcha.models import User, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        first_user_id, second_user_id = list(map(int, self.room_name.split('_')))
        try:
            user_1 = User.objects_.get(id=first_user_id)
        except Exception:
            raise Http404(f"Пользователя с данным id ({first_user_id}) не существует в базе")
        try:
            user_2 = User.objects_.get(id=second_user_id)
        except Exception:
            raise Http404(f"Пользователя с данным id ({second_user_id}) не существует в базе")
        self.user_1_id, self.user_2_id = user_1.id, user_2.id

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
        if text_data_json['global_user_id'] == self.user_1_id:
            type_ = Message.TO_1_2
        else:
            type_ = Message.TO_2_1
        Message(
            user_1_id=self.user_1_id,
            user_2_id=self.user_2_id,
            message=message,
            type=type_
        ).save()

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
