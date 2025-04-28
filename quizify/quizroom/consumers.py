from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import DenyConnection
import json,asyncio
from django.core.cache import cache
import time
from .quiz_master import start_quiz_master
# redeclaring the cache function and making them asynchronous

@sync_to_async
def get_cache(key):
    return cache.get(key)

@sync_to_async
def set_cache(key, value):
    return cache.set(key, value)

class quiz_consumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("[quiz_consumer] trying to connect...")
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
                dict[self.session_id]=self.username
                dict=cache.set(f"master:{self.room_name}_current_participants",dict)
                print("[quiz_consumer] participant updated")
                
            await self.accept()
            await self.update_lobby()
            await self.sync_time()
            await self.send(json.dumps({"update_on_connect":self.cached_data}))
            await self.send_state()
        else:
            DenyConnection("connect is not authorized")

    #send state message either through room group or by explicitly calling it
    async def update_lobby(self):
        await self.channel_layer.send(
            cache.get(f"master:{self.room_name}_host_channel_name"),
            {
                "type":"update.lobby.host",
                "lobby_data":list(cache.get(f"master:{self.room_name}_current_participants").values())
            }
        )
        print("[quiz_consumer] lobby update sent")
        
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
        question=self.question
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
    
    async def send_question(self,quiz_data,time):
        user_data=cache.get(f"participant:{self.session_id}")
        data={
            "question":quiz_data["text"],
            "options":quiz_data["options"],
            "duration":quiz_data["duration"],
            "time_stamp":time,
            "past_answers": user_data["answers"],
            "score":user_data["score"],
            "leader_board":user_data["leader_board"]
        }
        await self.send(json.dumps({"question_data":data}))
    
    async def sync_time(self):
        await self.send(json.dumps({"sync_time":time.time()}))
    
    async def disconnect(self, close_code):
        print(f"connection closed {close_code} disconnecting from {self.scope["path"]}")
        dict=cache.get(f"master:{self.room_name}_current_participants")
        try:
            dict.pop(self.session_id,None)
        except:
            pass
        dict=cache.set(f"master:{self.room_name}_current_participants",dict)
        await self.update_lobby()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        response = text_data_json["quiz_response"]
        print(response)
        if response not in ["A","B","C","D"]:
            return 
        q_state=await self.get_question_state()
        print(q_state)
        if q_state=="active" and not self.answered:
            d=cache.get(f"participant:{self.session_id}")
            d["answers"][self.question_index]=response
            cache.set(f"participant:{self.session_id}",d)
            self.answered=True      
            print(d)

    # Receive message from room group
    async def update_question(self, event):
        self.answered=False
        self.question=event["question"]
        self.question_index=self.question["index"]
        await self.send_question(event["question"],event["timestamp"])

    async def check_answer(self,event):
        await self.send_state()
        data=cache.get(f"participant:{self.session_id}")
        score=data["score"]
        self.qi=event["index"] # qusetion index from master
        if self.qi in data["answers"]:
            if data["answers"][self.qi]==event["ans"]:
                data["score"]+=event["points"]
                score=data["score"]
                # updating the participant cache
                cache.set(f"participant:{self.session_id}",data)
        # updating the score in main cache
        d_temp=cache.get(f"master:{self.room_name}_scores")
        d_temp[self.session_id]=score
        cache.set(f"master:{self.room_name}_scores",d_temp)
        print("check answer current leader board",d_temp)


    async def quiz_finished(self,event):
        self.send(json.dumps({"quiz_closed":"end","final_standings":cache.get(f"master:{self.room_name}_leader_board")}))
        print("final standings",cache.get(f"master:{self.room_name}_leader_board"))
        self.close()

class waiting_for_host(AsyncWebsocketConsumer):
    async def connect(self):
        print("[waiting...] connection process initiated")
        if (self.scope["session"]["verified"]):
            self.room_name = self.scope["session"]["quizid"]
            self.master_instance=None
            self.room_group_name = f"quizroom_{self.room_name}_announcement"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        
    async def start_quiz(self,event):
        await self.send(json.dumps({"status":"started"}))
        await self.close()
        
class host_management(AsyncWebsocketConsumer):
    async def connect(self):
        print("[host_management] trying to connect...")
        if self.scope["session"]["host_verified"]:
            self.room_name=self.scope["session"]["room_id"]
            self.room_group_name= f"quizroom_host:{self.room_name}"
            await self.accept()
            data1=cache.get(f"self.room_group_name_status")
            data2=cache.get(f"self.room_group_name_lobby")
            data3=cache.get(f"self.room_group_name_leader_board")
            if data1:
                print("state_found",data1)
                await self.send(json.dumps({"update_from_cache_status":data1}))
            if data2:
                print("state_found",data2)
                await self.send(json.dumps({"update_from_cache_lobby":data2}))
            if data3:
                print("state_found",data3)
                await self.send(json.dumps({"update_from_cache_leader_board":data3}))
            
        else:
            DenyConnection("host validation failed")
            
    async def receive(self, text_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            if message=="start_quiz_lobby":
                self.master_instance=await start_quiz_master(self.room_name,self.channel_name)
            elif message=="start_quiz":
                if self.master_instance:
                    asyncio.create_task(self.master_instance.start_quiz())
                else:
                    self.master_instance=await start_quiz_master(self.room_name,self.channel_name)
    
    async def update_cache_lobby(self,lobby):
        print("state updated")
        cache.set(f"{self.room_group_name}_lobby",lobby)      
    async def update_cache_leader(self,leader):
        print("state updated")
        cache.set(f"{self.room_group_name}_leader",leader)      
    async def update_cache_status(self,status):
        print("state updated")
        cache.set(f"{self.room_group_name}_status",status)      
    
    async def waiting_lobby_started(self,event):
        await self.update_cache_status("waiting_lobby_started")
        await self.send(json.dumps({"status":"waiting_lobby_started"}))
        
    
    async def quiz_started_host(self,event):
        await self.update_cache_status("Quiz_started")
        await self.send(json.dumps({"status":"Quiz_started"}))
       
    
    async def update_lobby_host(self,event):
        await self.update_cache_lobby(event["lobby_data"])
        await self.send(json.dumps({"update_lobby":event["lobby_data"]}))
        
    
    async def update_leader_board(self,event):
        await self.update_cache_leader(event["leader_board"])
        await self.send(json.dumps({"update_leader":event["leader_board"]}))
        
        
    async def quiz_finished_host(self,event):
        await self.update_cache_status("quiz ended")
        await self.send(json.dumps({"status":"quiz ended"}))
        await self.update_cache_status("quiz ended")
    
    async def update_question_host(self,event):
        await self.send(json.dumps({"update_question":event["question"]}))
    
    async def disconnect(self, close_code):
        print(f"connection closed{close_code} disconnecting from {self.scope["path"]}")
    