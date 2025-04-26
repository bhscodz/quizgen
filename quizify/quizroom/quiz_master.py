# quiz_master.py
import time
import asyncio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from .models import QuizRoom, Question

class QuizMaster:
    def __init__(self, quiz_id,host_channel_name):
        self.quiz_id = quiz_id
        self.room=QuizRoom.objects.get(quiz_id=quiz_id)
        self.room_group_name = f"quizroom_{quiz_id}"
        self.host_channel_name=host_channel_name
        self.channel_layer = get_channel_layer()
        self.cache_prefix = f"master:{quiz_id}"
        self.questions = [] 

    def load_questions(self):
        # Load questions from DB
        self.questions = list(Question.objects.filter(room=self.room).order_by('pk'))
        print(f"[QuizMaster] Loaded {len(self.questions)} questions.")

    def prepare_cache(self):
        # Reset quiz state
        cache.set(f"{self.cache_prefix}_current_question", None)
        cache.set(f"{self.cache_prefix}_scores", {}) # Dict of user_id/session -> score
        cache.set(f"{self.cache_prefix}_current_participants", {})  # Dict of user_id/session -> username
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
        self.load_questions()
        self.prepare_cache()
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
        data_participants=cache.get(f"{self.cache_prefix}_participants")
        data_scores_sorted=sorted(data_scores,key=lambda x:data_scores[x])
        leader_board={data_participants[x]:data_scores_sorted[x] for x in data_scores_sorted}
        cache.set(f"{self.cache_prefix}_leader_board",leader_board)
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
                    "ans":question.correct_option
                }
            )
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


# To run inside an async context (e.g., async Django mgmt command)
async def start_quiz_master(quiz_id,host_channel_name):
    master = QuizMaster(quiz_id,host_channel_name)
    await master.run_quiz()
    return master
    

# If you want to test:
# asyncio.run(start_quiz_master(1))
