#!/bin/sh

# Setup directories for diff audio formats
audio_dir_name="/data/audio"
transcriptions_dir_name="/data/transcriptions"
video_metadata_dir_name="/data/metadata"
mkdir -p $transcriptions_dir_name
mkdir -p $video_metadata_dir_name

insanely_fast_whisper_bin="/root/.local/share/pipx/venvs/insanely-fast-whisper/bin/insanely-fast-whisper"

# Due to machine memory and disk constraints, parallel runs out of memory when running through a file of 20+ lecture playlists
# Instead, we'll chunk the links input into separate files and go through each chunk sequentially
for file in "$1"/*; do
    # mkdir -p $processed_audios_dir_name
    mkdir -p $audio_dir_name
    # Download YT audio data from links text file as .wav files (by line in parallel)
    parallel -q -j+0 --progress -a $file yt-dlp --extract-audio --audio-format wav --audio-quality 0 --restrict-filenames  --write-info-json
    mv *.wav $audio_dir_name/
    mv *.info.json $video_metadata_dir_name/

    echo "Downloaded and processed audio for links in $file!"

    # Transcribe audio via insanely-fast-whisper model (only works on CUDA or Mac devices)
    ls $audio_dir_name | xargs -I {} basename {} .wav | xargs -I {} $insanely_fast_whisper_bin \
        --file-name "$audio_dir_name/{}.wav" \
        --batch-size 24 \
        --language "English" \
        --task transcribe \
        --transcript-path "$transcriptions_dir_name/$(basename {})"

    echo "Transcribed audio for links in $file!"

    rm -rf $audio_dir_name
done
