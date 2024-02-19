"""
Pull tasks from Redis queue/instance in fly.io
"""
import json
from typing import Any


REDIS_URL = "redis://default:d0ac64668d6e43cea9c1c4fe13f8e60f@fly-transcription_tasks.upstash.io:6379"



def transcribe_video(task: Any) -> None:
    # TODO: Run insanely-fast-whisper via Python API here
    pass


def exec_task():
    redis_client = redis.from_url(LOCAL_REDIS_URL)
    task_info = json.loads(redis_client.get())
    module_name = task_info["module"]
    fn_name = task_info["function_name"]
