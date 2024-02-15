# Video Transcription Pipeline

* Will be implemented as a DAG pipeline, Redis message queue, and run on a set of Kubernetes/Fly.io workers
* We could use Google Cloud's or AWS's managed STT services, but that is much more expensive.
  * Google Cloud: $.009 per 15 secs; .009 * (3600*24/15) = $51.84 per hour of video
  * Fly GPU A100 (40GB) pricing: $2.50 per hour
  * ~20.74x cheaper to run on GPU cloud!

## Useful Fly Commands
```bash
fly status  # Check if machines are running
fly machine start  # Start machine again
fly machine stop  # Stop machine if running
fly deploy  # Deploys app (according to fly.toml and Dockerfile)
fly ssh console  # Run cmds directly on fly machine (after machine is started)
```

## Ideas

* If we decide to use GPUs for the Kubernetes workers, we can run [this Whisper model code](https://github.com/Vaibhavs10/insanely-fast-whisper) on a GPU worker
* [Kubernetes Parallel Processing Via Work Queue](https://kubernetes.io/docs/tasks/job/fine-parallel-processing-work-queue/)
* [Fly.io Async Workers](https://fly.io/blog/python-async-workers-on-fly-machines/)
* [Pinterest Async Computing Platform](https://medium.com/pinterest-engineering/pacer-pinterests-new-generation-of-asynchronous-computing-platform-5c338a15d2a0)
* [Example System Design of Audio Transcription](https://blog.salad.com/whisper-large-v2-benchmark/)
* [Song Lyric Extraction via Whisper and Spleeter](https://www.digitalocean.com/community/tutorials/how-to-make-karaoke-videos-using-whisper-and-spleeter-ai-tools)
* [Paperspace Notebooks](https://www.paperspace.com/notebooks) to try out GPU code for free
