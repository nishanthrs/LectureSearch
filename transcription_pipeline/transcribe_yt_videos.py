"""
Pull tasks from Redis queue/instance in fly.io/Upstash or PC
"""
import json
import os
import redis
import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available
import typesense
from typing import Any, Dict, List, Optional
import yt_dlp


# TODO: Set these as Fly secrets: https://fly.io/docs/reference/secrets/ or env vars in Dockerfile
COLLECTION_NAME = "educational_video_transcriptions"
UPSTASH_REDIS_URL = "redis://default:dc4072d39b6745739f01b6c14cc2a658@fly-lecturesearch-web-redis.upstash.io:6379"
QUEUE_NAME = "transcription_tasks_queue"

TranscriptionChunks = List[Dict[str, Any]]


def _find_file(ext: str) -> Optional[str]:
    """Find first file in curr dir with specific extension"""
    for file in list(filter(lambda f: os.path.isfile(f), os.listdir("."))):
        if file.endswith(ext):
            return file
    return None


def _remove_file(ext: str) -> None:
    """Remove all files in curr dir of specific extension"""
    for file in list(filter(lambda f: os.path.isfile(f), os.listdir("."))):
        if file.endswith(ext):
            os.remove(file)

def extract_audio_and_metadata_from_video(yt_url: str) -> str:
    """Download YT video as audio file"""
    yt_dlp_opts = {
        "format": "wav/bestaudio/best",
        "postprocessors": [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        "prefer_ffmpeg": True,
        "audioquality": 0,
        "restrictfilenames": True,
        "writeinfojson": True,
    }
    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
        error_code = ydl.download(yt_url)
        if error_code != 0:
            print(f"Error: {error_code} in downloading YT video: {yt_url}")

    audio_filepath = _find_file(".wav")
    if audio_filepath is None:
        raise Exception("No audio filepath found!")
    metadata_filepath = _find_file(".info.json")
    if metadata_filepath is None:
        raise Exception(f"No metadata filepath found!")
    return (audio_filepath, metadata_filepath)


def transcribe_video(audio_filepath: str) -> TranscriptionChunks:
    """Transcribe audio from audio_filepath"""
    generate_kwargs = {
        "task": "transcribe",
        "language": "en",  # Only transcribe English videos
    }
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3",
        torch_dtype=torch.float16,
        device_map="cuda:0",
        model_kwargs={"attn_implementation": "flash_attention_2"} 
        if is_flash_attn_2_available() 
        else {"attn_implementation": "sdpa"},
        generate_kwargs=generate_kwargs,
    )
    transcription_output = pipe(
        audio_filepath,
        chunk_length_s=30,
        batch_size=12,  # VRAM is a constraint (12 GB isn't enough for a batch size of 24)
        return_timestamps=True,
    )
    print(f"Transcription output: {transcription_output['chunks']}")
    return transcription_output["chunks"]


def init_search_client() -> typesense.Client:
    """Init Typesense client to communicate with Typesense server"""
    client = typesense.Client({
        "api_key": os.environ["TYPESENSE_API_KEY"],
        "nodes": [{
            "host": "typesense-search-idx.fly.dev",
            "port": "443",
            "protocol": "https",
        }],
        "connection_timeout_seconds": 2.0,
    })
    return client


def init_collection(client: typesense.Client) -> None:
    """Initialize index/collection in Typesense server"""
    video_transcription_schema = {
        "name": COLLECTION_NAME,
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "video_id", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "channel", "type": "string"},
            {"name": "upload_date", "type": "string"},
            {"name": "channel_follower_count", "type": "int32"},
            {"name": "view_count", "type": "int32"},
            {"name": "like_count", "type": "int32"},
            {"name": "start_time", "type": "int32"},
            {"name": "end_time", "type": "int32"},
            {"name": "content", "type": "string"},
            {"name": "thumbnail_url", "type": "string"},
        ],
        "default_sorting_field": "channel_follower_count",
    }
    init_collection_response = client.collections.create(video_transcription_schema)
    print(f"Initialized new collection: {init_collection_response}")


def upload_transcription_data_to_typesense(
    typesense_client: typesense.Client, transcription_chunks: TranscriptionChunks, metadata_filepath: str
) -> None:
    """Index data from transcription files to typesense collection"""
    with open(metadata_filepath, 'r') as fd:
        video_metadata = json.load(fd)

    transcription_docs = []
    for chunk_idx, chunk in enumerate(transcription_chunks):
        start_ts, end_ts = chunk["timestamp"]
        print(f"Timestamps: {start_ts, end_ts}")
        text = chunk["text"]
        
        # Create and upload to Typesense collection
        try:
            transcription_doc = {
                "id": f"{video_metadata['id']}_{chunk_idx}",
                "video_id": video_metadata["id"],
                "title": video_metadata["title"],
                "channel": video_metadata["channel"],
                "upload_date": video_metadata["upload_date"],
                "channel_follower_count": video_metadata["channel_follower_count"],
                "view_count": video_metadata["view_count"],
                "like_count": video_metadata["like_count"],
                "start_time": int(round(start_ts, 0)) if start_ts is not None else 0,
                "end_time": int(round(end_ts, 0)) if end_ts is not None else 0,
                "content": text,
                "thumbnail_url": video_metadata["thumbnail"],
            }
            transcription_docs.append(transcription_doc)
        except KeyError as e:
            print(f"Could not find key {e} in metadata file {metadata_filepath}. Skipping this video.")
            continue

    _remove_file(".wav")
    _remove_file(".info.json")

    # For some dumbass reason, the Typesense import endpoint always returns a HTTP 200 OK response, even if the import failed
    # So we have to manually check the response to see if it's successful: https://typesense.org/docs/0.22.2/api/documents.html#index-multiple-documents
    print(f"Transcription docs: {transcription_docs}")
    responses = typesense_client.collections[COLLECTION_NAME].documents.import_(
        transcription_docs, {"action": "upsert"}
    )
    for response in responses:
        if not response["success"]:
            print(f"Failed to index doc: {response}")


def exec_task():
    # redis_client = redis.Redis(
    #     host="fly-lecturesearch-web-redis.upstash.io",
    #     port=6379,
    #     password="dc4072d39b6745739f01b6c14cc2a658",
    #     decode_responses=True,
    # )
    # # TODO: Experiment with popping multiple tasks off the queue and running downloading/transcription in parallel
    # task_data = redis_client.lpop(QUEUE_NAME)
    # if task_data is not None:
    #     task_info = json.loads(task_data)
    #     task_id = task_info["id"]
    #     video_id = task_info["video_id"]
    #     print(f"Popped task {task_id}: {video_id}")
    
    # TODO: Run hardcoded version for now; remove later
    audio_filepath, metadata_filepath = extract_audio_and_metadata_from_video(
        "https://www.youtube.com/watch?v=I2ZK3ngNvvI"
    )

    transcription_chunks = transcribe_video(audio_filepath)

    typesense_client = init_search_client()
    # typesense_client.collections[COLLECTION_NAME].delete()
    try:
        init_collection(typesense_client)
    except typesense.exceptions.ObjectAlreadyExists:
        pass
    upload_transcription_data_to_typesense(typesense_client, transcription_chunks, metadata_filepath)


if __name__ == "__main__":
    exec_task()