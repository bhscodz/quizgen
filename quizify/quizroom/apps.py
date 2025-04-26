from django.apps import AppConfig
import redis

class QuizroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quizroom'
    def ready(self):
        try:
            r = redis.Redis(host='localhost', port=6379, db=1)
            # Use a key prefix to delete only related keys
            prefixes = ["master:*", "quizroom_host:*", "participant:*"]
            for pattern in prefixes:
                for key in r.scan_iter(pattern):
                    r.delete(key)
            print("Redis cache (app-specific keys) cleared on server reload.")
        except Exception as e:
            print(f"⚠️ Redis partial flush failed: {e}")