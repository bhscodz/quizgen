from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import DenyConnection
import json
from django.core.cache import cache

class quiz_consumer(AsyncWebsocketConsumer):
    async def connect(self):
        if(self.scope["session"]["verified"]):
            self.user=self.scope["user"]
            self.started=False
            self.session_id=self.scope["session"].session_key
            self.cached_data=cache.get(f"participant:{self.session_id}")
            self.username=self.cached_data["username"]
            self.guest=not self.user.is_authenticated
            self.room_name = self.scope["session"]["quizid"]
            self.room_group_name = f"quizroom_{self.room_name}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self.send_state()
        else:
            await DenyConnection("connect is not authorized")

    #send state message either through room group or by explicitly calling it
    async def send_state(self,quiz_data):
        if self.started:
            user_data=cache.get(f"participant:{self.session_id}")
            data={
                "question":quiz_data["question"],
                "options":quiz_data["options"],
                "duration":quiz_data["duration"],
                "past_answers": user_data["answers"],
                "score":user_data["score"],
                "servertime":quiz_data["start_time"]
            }
        else:
            self.send(json.dumps({"status_message":"started_false"}))
    
    async def sync_time(self):
        data=cache.get(f"master:{self.session_id}")
        self.send(json.dumps({"sync_time":data["start_time"]}))
    
    async def disconnect(self, close_code):
        print(f"connection closed {close_code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        response = text_data_json["quiz_response"]

    # Receive message from room group
    async def update_question(self, event):
        if not self.started:
            self.started=True
        cache.set(self.session_id,{})
        await self.send_state()