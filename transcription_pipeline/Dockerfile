FROM ubuntu:22.04

# Install Ubuntu and CUDA pkgs: https://fly.io/docs/gpus/getting-started-gpus/#installing-nvidia-libraries
RUN apt update \
    && apt install -y ca-certificates git parallel wget ffmpeg python3.10 python3-pip python3.10-venv \
    && wget -qO /cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
    && dpkg -i /cuda-keyring.deb \
    && apt update -q \
    && apt install -y --no-install-recommends cuda-nvcc-12-2 libcublas-12-2 libcudnn8

# Install pipx, insanely-fast-whisper
RUN pip install pipx \
    && pipx install insanely-fast-whisper --python python3.10 \
    && pipx ensurepath

# Install flash-attn pkg (used to optimize insanely-fast-whisper)
RUN pipx runpip insanely-fast-whisper install wheel \
    && pipx runpip insanely-fast-whisper install flash-attn --no-build-isolation

# Install yt-dlp to path: /usr/local/bin
RUN wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp \
    && chmod a+rx /usr/local/bin/yt-dlp

# Set working directory on Docker container to /app and move all files from transcription_pipeline/ dir to there
WORKDIR /app
COPY . /app
RUN chmod u+x /app/gen_video_ids.sh
RUN chmod u+x /app/transcribe_yt_videos.sh
RUN chmod u+x /app/batch_transcription.sh
CMD ["./batch_transcription.sh"]
