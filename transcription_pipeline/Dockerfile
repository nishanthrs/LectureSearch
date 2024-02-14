FROM ubuntu:22.04

# Install Ubuntu pkgs
RUN apt update \
    && apt install -y ca-certificates curl wget ffmpeg python3.10 python3-pip python3.10-venv \
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
COPY gen_video_ids.sh /app/gen_video_ids.sh
COPY transcribe_yt_videos.sh /app/transcribe_yt_videos.sh

RUN ./gen_video_ids.sh "https://www.youtube.com/@mitocw/playlists" "\s(6\.|18\.)" cs_math_mit_ocw_playlist_ids.txt 10
CMD ["./transcribe_audio.sh", "playlist_ids_files"]
