# quiz_master.py
import time
import asyncio
from asgiref.sync import async_to_sync,sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.core.cache import cache
from .models import QuizRoom, Question

@database_sync_to_async
def get_room(quiz_id):
    return QuizRoom.objects.get(quiz_id=quiz_id)
class QuizMaster:
    def __init__(self, quiz_id,host_channel_name):
        self.quiz_id = quiz_id
        self.room_group_name = f"quizroom_{quiz_id}"
        self.host_channel_name=host_channel_name
        self.channel_layer = get_channel_layer()
        self.cache_prefix = f"master:{quiz_id}"
        self.questions = [] 

    async def read_sync_db(self):
        self.room=await get_room(self.quiz_id)
    
    async def load_questions(self):
        # Load questions from DB
        self.questions = await database_sync_to_async(lambda: list(Question.objects.filter(room=self.room).order_by('pk')))()
        print(f"[QuizMaster] Loaded {len(self.questions)} questions.")

    async def prepare_cache(self):
        # Reset quiz state
        cache.set(f"{self.cache_prefix}_current_question", None)
        cache.set(f"{self.cache_prefix}_scores", {}) # Dict of user_id/session -> score
        cache.set(f"{self.cache_prefix}_current_participants", {})  # Dict of user_id/session -> username
        cache.set(f"{self.cache_prefix}_all_participants", {})  # Dict of user_id/session -> username
        cache.set(f"{self.cache_prefix}_master_is_on","waiting")
        cache.set(f"{self.cache_prefix}_leader_board",{})
        cache.set(f"{self.cache_prefix}_host_channel_name",self.host_channel_name)
        print("[QuizMaster] Cache initialized.")

    async def send_question(self, question, index):
        question_data = {
            "id": question.pk,
            "text": question.question_text,
            "answer":question.correct_option,
            "options": [question.option_a, question.option_b, question.option_c, question.option_d],
            "points": question.points,
            "duration": question.duration,
            "server_time":time.time(),
            "index":index
        }

        # Set in cache for participant sync/fetch
        cache.set(f"{self.cache_prefix}_current_question", question_data, timeout=question.duration+10)

        # Send over WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "update.question",
                "question": question_data,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )
        await self.channel_layer.send(
            self.host_channel_name,
            {
                "type": "update.question.host",
                "question": question_data,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )
        print(f"[QuizMaster] Sent question {index + 1}")

    async def run_quiz(self):
        print("3")
        await self.read_sync_db()
        await self.load_questions()
        print("4")
        await self.prepare_cache()
        print("5")
        await self.channel_layer.send(
            self.host_channel_name,
            {
                "type":"waiting.lobby.started"
            }
        )
        print("[quizMaster] questions loaded.. cache prepared ... waiting to start..")
        await self.channel_layer.group_send(
                self.room_group_name+"_announcement",
                {
                    "type":"start.quiz"
                }
            )
        
    async def calc_leader_board(self):
        data_scores=cache.get(f"{self.cache_prefix}_scores")
        data_participants=cache.get(f"{self.cache_prefix}_current_participants")
        data_scores_sorted = dict(sorted(data_scores.items(), key=lambda item: item[1], reverse=True))
        print(data_scores_sorted)
        leader_board={}
        for i in data_scores_sorted:
            if i in data_participants:
                leader_board[data_participants[i]]=data_scores_sorted[i]
        #leader_board={data_participants[x]:data_scores_sorted[x] for x in data_scores_sorted}
        cache.set(f"{self.cache_prefix}_leader_board",leader_board)
        print("[quiz_master] leader board",leader_board)
        await self.channel_layer.send(
            self.host_channel_name,
            {
                "type":"update.leader.board",
                "leader_board":leader_board
            }
        )
        print("[quiz_master]:leader_board_updated!")
        
    async def start_quiz(self):
        cache.set(f"{self.cache_prefix}_master_is_on","started")
        await self.channel_layer.send(
            self.host_channel_name,
            {
                "type":"quiz.started.host"
            }
        )
        for index, question in enumerate(self.questions):
            await self.send_question(question, index)
            await asyncio.sleep(question.duration)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type":"check.answer",
                    "ans":question.correct_option,
                    "points":question.points,
                    "index":index
                }
            )
            await asyncio.sleep(2)
            await self.calc_leader_board()
            await asyncio.sleep(2)

        # Mark quiz as finished
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "quiz.finished",
            },
        )
        await self.channel_layer.send(
            self.host_channel_name,
            {
                "type": "quiz.finished.host",
            },
        )

        cache.set(f"{self.cache_prefix}_master_is_on","end")
        print("[QuizMaster] Quiz finished.")
        asyncio.sleep(20)
        print("[cleaaning cache]")
        keys_to_clear = [
            f"{self.cache_prefix}_current_question",
            f"{self.cache_prefix}_scores",
            f"{self.cache_prefix}_current_participants",
            f"{self.cache_prefix}_master_is_on",
            f"{self.cache_prefix}_leader_board",
            f"{self.cache_prefix}_host_channel_name",
            f"quizroom_host:{self.quiz_id}_status",
            f"quizroom_host:{self.quiz_id}_lobby",
            f"quizroom_host:{self.quiz_id}_leader_board",
            
        ]
        participant=cache.get(f"{self.cache_prefix}_all_participants")
        for i in participant:
            keys_to_clear.append(f"participant:{i}")
        
    
        for key in keys_to_clear:
            print(cache.delete(key),key)
            
        



# To run inside an async context (e.g., async Django mgmt command)
async def start_quiz_master(quiz_id,host_channel_name):
    print("1")
    master = QuizMaster(quiz_id,host_channel_name)
    print("2")
    await master.run_quiz()
    return master
    

# If you want to test:
# asyncio.run(start_quiz_master(1))
