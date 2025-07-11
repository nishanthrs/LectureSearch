# Video Transcription Pipeline

## Overview
* Will be implemented as an Airflow DAG pipeline deployed as a Docker container:
  * Transcribes via fasterwhisper
  * Generates embeddings via encoder model (e.g. sentence-transformers (SBERT), ModernBert, local LLM that can fit on GPU worker (e.g. Qwen3), or embeddings APIs from Gemini, Cohere, etc.)
    * [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
  * Writes to [local Parquet files / Polars dataframes](https://minimaxir.com/2025/02/embeddings-parquet/) or local/remote vector database (Postgres: pgvector)
  * Get working locally on PC with local Polars dataframes, sentence-transformers models or Qwen3 embeddings models, and faster-whisper model -> use remote Postgres database -> deploy to GPU worker
 
## Video Transcription
* We could use Google Cloud's or AWS's managed STT services, but that is much more expensive.
  * Google Cloud: $.009 per 15 secs; .009 * (3600*24/15) = $51.84 per hour of video
  * Fly GPU A100 (40GB) pricing: $2.50 per hour
  * ~20.74x cheaper to run on GPU cloud!
  * Based on the benchmarks for [`insanely-fast-whisper`](https://github.com/Vaibhavs10/insanely-fast-whisper?tab=readme-ov-file), via batching and fp16 and bettertransformer framework, we can transcribe at 30x realtime.
  * That means we can transcribe 30(60) = 1800 mins of audio in an hour or for $2.50. That means ~30 videos of 1 hr lectures transcribed at $2.50. Even if this is an optimistic estimate, that's significantly cheaper than any managed service. 
  
## Installing Nvidia Drivers and CUDA on Ubuntu PC

Was a huge pain in the ass to download Nvidia drivers on my Ubuntu PC; I've lost count on how many times I've had to restart and reboot in recovery mode:

* Had to download nvidia-driver-525
  * By default, Ubuntu will download the one with -server. This is not correct, there is no GUI support for this! The same goes for the -open driver as well.
  * Initially tried downloading nvidia-driver-535; that didn't work
  * Also had to [disable nouveau drivers](https://askubuntu.com/questions/841876/how-to-disable-nouveau-kernel-driver) before installing and rebooting
  * Very useful [reference](https://gist.github.com/MihailCosmin/affa6b1b71b43787e9228c25fe15aeba) for all the installation and cleanup commands
  * Maybe I'll try upgrading drivers to nvidia-driver-545 somewhere down the line
* Installing CUDA was quite simple
  * Followed [instructions on Nvidia site](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=20.04&target_type=deb_local)
  * Had to be careful to download right CUDA version (12.0.1) for nvidia-driver-525

Even installing these packages for the Dockerfile from a base Ubuntu image on Fly.io GPU servers was a bit of a pain (not as much as installing them locally though).

## Useful Fly Commands

```bash
# Run within same dir as fly.toml; otherwise, auth and cmds won't work!
fly status  # Check if machines are running
fly machine start  # Start machine again
fly machine stop  # Stop machine if running
fly deploy  # Deploys app (according to fly.toml and Dockerfile)
fly ssh console  # Run cmds directly on fly machine (after machine is started)
fly ssh console -a video-transcription -C "cat /data/transcriptions/Lecture_1_Part_1_-_Introduction_and_Motivation-[0YqjeqLhDDE]"
LPOP transcription_task_queue  # redis-cli cmd to get data
```

## Ideas

* If we decide to use GPUs for the Kubernetes workers, we can run [this Whisper model code](https://github.com/Vaibhavs10/insanely-fast-whisper) on a GPU worker
* [Kubernetes Parallel Processing Via Work Queue](https://kubernetes.io/docs/tasks/job/fine-parallel-processing-work-queue/)
* [Fly.io Async Workers](https://fly.io/blog/python-async-workers-on-fly-machines/)
* [Pinterest Async Computing Platform](https://medium.com/pinterest-engineering/pacer-pinterests-new-generation-of-asynchronous-computing-platform-5c338a15d2a0)
* [Example System Design of Audio Transcription](https://blog.salad.com/whisper-large-v2-benchmark/)
* [Song Lyric Extraction via Whisper and Spleeter](https://www.digitalocean.com/community/tutorials/how-to-make-karaoke-videos-using-whisper-and-spleeter-ai-tools)
* [Paperspace Notebooks](https://www.paperspace.com/notebooks) to try out GPU code for free
