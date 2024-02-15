FROM ubuntu:22.04

# Install Ubuntu and CUDA pkgs
RUN apt update \
    && apt install -y ca-certificates curl parallel wget ffmpeg python3.10 python3-pip python3.10-venv \
    && wget -qO /cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
    && dpkg -i /cuda-keyring.deb \
    && apt update -q \
    && apt install -y --no-install-recommends cuda-nvcc-12-2 libcublas-12-2 libcudnn8

# Install pipx, insanely-fast-whisper, yt-dlp
RUN pip install pipx \
    && pipx ensurepath \
    && pipx install insanely-fast-whisper --force --pip-args="--ignore-requires-python" \
    && curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp \
    && chmod a+rx ~/.local/bin/yt-dlp

WORKDIR /app
COPY . /app
RUN chmod u+x /app/gen_video_ids.sh
RUN chmod u+x /app/transcribe_yt_videos.sh
RUN chmod u+x /app/batch_transcription.sh
RUN echo $(pwd)
CMD ["./batch_transcription.sh"]
