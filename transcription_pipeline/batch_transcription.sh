#!/bin/sh

./gen_video_ids.sh "https://www.youtube.com/@mitocw/playlists" "\s(6\.|18\.)" cs_math_mit_ocw_playlist_ids.txt 10
echo "Generating playlist/video IDs done! Moving on to transcription..."
./transcribe_yt_videos.sh playlist_ids_files
echo "Transcribed all videos from all playlists in playlist_ids_files dir!"
