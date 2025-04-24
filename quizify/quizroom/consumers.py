from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import DenyConnection
import json
from django.core.cache import cache
import time
# redeclaring the cache function and making them asynchronous

@sync_to_async
def get_cache(key):
    return cache.get(key)

@sync_to_async
def set_cache(key, value):
    return cache.set(key, value)

class quiz_consumer(AsyncWebsocketConsumer):
    async def connect(self):
        if(self.scope["session"]["verified"]) and cache.get(f"master:{self.scope["session"]["quizid"]}_master_is_on"):
            self.user=self.scope["user"]
            self.session_id=self.scope["session"].session_key
            self.question_index=None
            self.answered=False
            self.cached_data=cache.get(f"participant:{self.session_id}")
            self.username=self.cached_data["username"]
            self.guest=not self.user.is_authenticated
            self.room_name = self.scope["session"]["quizid"]
            self.state=cache.get(f"master:{self.room_name}_master_is_on")
            self.room_group_name = f"quizroom_{self.room_name}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            if self.state != "end":
                dict=cache.get(f"master:{self.room_name}_current_participants")
                dict[f"pariticapnt:{self.session_id}"]=self.username
                dict=cache.set(f"master:{self.room_name}_current_participants",dict)
            await self.accept()
            await self.sync_time()
            if self.scope["session"]["reconnected"]:
                await self.send(json.dumps({"update_on_reconnect":self.cached_data}))
            await self.send_state()
        else:
            DenyConnection("connect is not authorized")

    #send state message either through room group or by explicitly calling it
    async def send_state(self):
        state=self.state
        if self.state=="started" and self.get_question_state()=="active":
            await self.send(json.dumps({"state_message":"active_question"}))
            await self.send_question()
        elif self.state=="started" and (self.get_question_state()=="time_over" or self.get_question_state()=="no_question"):
            await self.send(json.dumps({"state_message":"wait_for_next"}))
        else:
            await self.send(json.dumps({"state_message":self.state}))
        
    
    async def get_question_state(self):
        question=cache.get(f"master{self.room_name}_current_question")
        if question:
            current=time.time()
            duration =question.get("duration")
            server_time =question.get("server_time")
            if duration>current-server_time:
                return "active"
            else:
                return "time_over"
        else:
            return "no_question"
    
    async def send_question(self,quiz_data):
        user_data=cache.get(f"participant:{self.session_id}")
        data={
            "question":quiz_data["question"],
            "options":quiz_data["options"],
            "duration":quiz_data["duration"],
            "past_answers": user_data["answers"],
            "score":user_data["score"],
            "leader_board":user_data["leader_board"]
        }
        await self.send(json.dumps({"question_data":data}))
    
    async def sync_time(self):
        await self.send(json.dumps({"sync_time":time.time()}))
    
    async def disconnect(self, close_code):
        print(f"connection closed {close_code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        response = text_data_json["quiz_response"]
        q_state=await self.get_question_state()
        if q_state=="active" and not self.answered:
            d=cache.get(f"participant:{self.room_name}")
            d["answers"][self.index]=response
            cache.set(f"participant:{self.room_name}",d)
            self.answered=True      

    # Receive message from room group
    async def update_question(self, event):
        self.answered=False
        self.question=event["question_data"]
        self.question_index=self.question.index
        if not self.started:
            self.started=True
        await self.send_question()

    async def check_answer(self):
        await self.send_state()
        data=cache.get(f"participant:{self.room_name}")
        score=data["score"]
        if self.index in data["answers"]:
            if data["answer"]["index"]==self.question.answer:
                data["score"]+=1
                score=data["score"]
                # updating the participant cache
                cache.set(f"participant:{self.room_name}",data)
        # updating the score in main cache
        d_temp=cache.get(f"master:{self.room_name}_scores")
        d_temp[self.room_name]=score
        cache.set(f"master:{self.room_name}_scores",d_temp)

    async def calc_leader_board(self):
        data_scores=cache.get(f"master:{self.room_name}_scores")
        data_participants=cache.get(f"master:{self.room_name}_participants")
        data_scores_sorted=sorted(data_scores,key=lambda x:data_scores[x])
        leader_board={data_participants[x]:data_scores_sorted[x] for x in data_scores_sorted}
        temp_cache= cache.get(f"participant:{self.room_name}")
        temp_cache["leader_board"]=leader_board
        cache.set(f"participant:{self.room_name}",temp_cache)


    async def quiz_finished(self):
        self.send(json.dumps({"quiz_closed":"end"}))
        self.close()

class waiting_for_host(AsyncWebsocketConsumer):
    async def connect(self):
        print("[waiting...] connection process initiated")
        if (self.scope["session"]["verified"]):
            self.room_name = self.scope["session"]["quizid"]
            self.room_group_name = f"quizroom_{self.room_name}_announcement"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        
    async def quiz_started(self):
        await self.send(json.dumps({"status":"started"}))
        await self.close()