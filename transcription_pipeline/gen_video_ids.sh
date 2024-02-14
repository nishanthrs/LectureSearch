yt-dlp --skip-download --flat-playlist --print "%(title)s ||| %(id)s" $1 | grep -E $2 | awk -F ' \\|\\|\\| ' '{print $2}' > $3

playlist_links_dir="playlist_ids_files"
mkdir -p $playlist_links_dir
filename=${3%.*}
# ext=${3#*.}
split -l $4 $3 "$playlist_links_dir/$filename."
