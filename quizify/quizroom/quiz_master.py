# quiz_master.py
import time
import asyncio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from .models import QuizRoom, Question

class QuizMaster:
    def __init__(self, quiz_id):
        self.quiz_id = quiz_id
        self.room=QuizRoom.objects.get(quiz_id=quiz_id)
        self.room_group_name = f"quizroom_{quiz_id}"
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
        print(f"[QuizMaster] Sent question {index + 1}")

    async def run_quiz(self):
        self.load_questions()
        self.prepare_cache()
        print("[quizMaster] questions loaded.. cache prepared ... waiting to start..")
        await self.channel_layer.group_send(
                self.room_group_name+"_announcement",
                {
                    "type":"start.quiz"
                }
            )
    
    async def start_quiz(self):
        cache.set(f"{self.cache_prefix}_master_is_on","started")
        for index, question in enumerate(self.questions):
            await self.send_question(question, index)
            await asyncio.sleep(question.duration)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type":"check.answer"
                }
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type":"calc.leader.board"
                }
            )
            await asyncio.sleep(2)

        # Mark quiz as finished
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "quiz.finished",
            },
        )
        cache.set(f"{self.cache_prefix}_master_is_on","end")
        print("[QuizMaster] Quiz finished.")


# To run inside an async context (e.g., async Django mgmt command)
async def start_quiz_master(quiz_id):
    master = QuizMaster(quiz_id)
    await master.run_quiz()

# If you want to test:
# asyncio.run(start_quiz_master(1))
