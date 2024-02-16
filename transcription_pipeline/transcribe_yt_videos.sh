#!/bin/sh

# Setup directories for diff audio formats
raw_audios_dir_name="raw_audios"
processed_audios_dir_name="processed_audios"
transcriptions_dir_name="transcriptions"
video_metadata_dir_name="metadata"
mkdir -p $raw_audios_dir_name
mkdir -p $processed_audios_dir_name
mkdir -p $transcriptions_dir_name
mkdir -p $video_metadata_dir_name

# Due to machine memory and disk constraints (Mac M1; 16 GB RAM; 512 GB SSD), parallel runs out of memory when running through a file of 20+ lecture playlists
# Instead, we'll chunk the links input into separate files and go through each chunk sequentially
for file in "$1"/*; do
    # Download YT audio data from links text file as .wav files (by line in parallel)
    parallel -q -j+0 --progress -a $file yt-dlp --ffmpeg-location /opt/local/bin/ffmpeg --extract-audio --audio-format wav --audio-quality 0 --restrict-filenames  --write-info-json
    # TODO: Currently an issue here! Remove CMD from Docker container, keep Fly machine open by editing fly.toml, and debug why this is occurring quickly
    mv *.wav $raw_audios_dir_name/
    mv *.info.json $video_metadata_dir_name/
    # Convert audio files to 16 khz (whisper.cpp only works on 16-bit wav files)
    parallel -j+0 ffmpeg -i "$raw_audios_dir_name/{}" -ar 16000 -ac 1 -c:a pcm_s16le "$processed_audios_dir_name/{.}.wav" ::: $(ls $raw_audios_dir_name)
    # Remove raw audio files
    rm -rf $raw_audios_dir_name

    echo "Downloaded and processed audio for links in $file!"

    # Transcribe audio via insanely-fast-whisper model (only works on CUDA or Mac devices)
    # TODO: Figure out how to use flash-attn arg and install it correctly in Dockerfile
    # (currently an issue with wheel pkg; consider pip installing that manually first in Dockerfile)
    ls $processed_audios_dir_name | xargs -I {} basename {} .wav | xargs -I {} insanely-fast-whisper \
        --file-name "$processed_audios_dir_name/{}.wav" \
        --batch-size 24 \
        --language "English" \
        --task transcribe \
        --transcript-path "$transcriptions_dir_name/$(basename {})"

    echo "Transcribed audio for links in $file!"
done
