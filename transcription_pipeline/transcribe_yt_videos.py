"""
Pull tasks from Redis queue/instance in fly.io/Upstash or PC
"""
import json
import redis
import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available
from typing import Any


UPSTASH_REDIS_URL = "redis://default:d0ac64668d6e43cea9c1c4fe13f8e60f@fly-transcription_tasks.upstash.io:6379"
QUEUE_NAME = "transcription_tasks_queue"


def transcribe_video(video_id: int) -> None:
    """
    1. Download YT video as audio file (TODO)
    2. Transcribe audio file
    3. Upload transcription to Typesense server or vector DB (TODO)
    """
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3", # select checkpoint from https://huggingface.co/openai/whisper-large-v3#model-details
        torch_dtype=torch.float16,
        device_map="cuda:0",
        model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
    )
    outputs = pipe(
        # "Advice_for_machine_learning_beginners_Andrej_Karpathy_and_Lex_Fridman-[I2ZK3ngNvvI].wav",
        "Getting_Started_With_CUDA_for_Python_Programmers-[nOxKexn3iBo].wav",
        chunk_length_s=30,
        batch_size=8,  # Ideal size: 24, but VRAM is a constraint (12 GB isn't enough for a batch size of 24)
        return_timestamps=True,
    )
    print(f"Transcription output: {outputs}")


def exec_task():
    redis_client = redis.Redis(
        host="fly-transcription_tasks.upstash.io",
        port=6379,
        password="d0ac64668d6e43cea9c1c4fe13f8e60f"
    )
    # TODO: Experiment with popping multiple tasks off the queue and running downloading/transcription in parallel
    task_info = json.loads(redis_client.lpop(QUEUE_NAME))
    task_id = task_info["id"]
    video_id = task_info["video_id"]
    print(f"Popped task {task_id}: {video_id}")
    transcribe_video(video_id)


if __name__ == "__main__":
    exec_task()