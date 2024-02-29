FROM ubuntu:22.04

# Install Ubuntu and CUDA pkgs: https://fly.io/docs/gpus/getting-started-gpus/#installing-nvidia-libraries
RUN apt update \
    && apt install -y ca-certificates git parallel wget ffmpeg python3.10 python3-pip \
    && wget -qO /cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
    && dpkg -i /cuda-keyring.deb \
    && apt update -q \
    && apt install -y --no-install-recommends cuda-nvcc-12-2 libcublas-12-2 libcudnn8

# Install pip pkgs to run python script to download, transcribe, and upload videos
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt && pip install flash-attn --no-build-isolation
CMD ["python3", "transcribe_yt_videos.py"]
