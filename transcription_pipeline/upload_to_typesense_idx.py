import json
import os
import pysrt
import typesense

"""
Output from insanely-fast-whisper:
{
    "speakers": [...],
    "chunks": [
        {
            "timestamp": [2136.44, 2138.44], 
            "text": " OK, well, we've got a good set of students"}
        }
    ],
    "text": "...",
}
"""


COLLECTION_NAME = "educational_video_transcriptions"

def init_search_client() -> typesense.Client:
    client = typesense.Client({
        "api_key": "xyz",
        "nodes": [{
            # TODO: Change to web server IP (GPU on private networking (Flycast app), web server on public networking)
            # This script will be run on Fly GPU, so need to figure out how to connect Fly GPU to web server on same private network
            # Web server on Fly.io, DigitalOcean, or AWS? Which cloud provider?
            # For now, run the web server on the Ubuntu PC, so just make sure that's on the same network as Fly GPU
            # Docs: https://fly.io/docs/networking/
            "host": "localhost",
            "port": "8108",
            "protocol": "http",
        }],
        "connection_timeout_seconds": 2.0,
    })
    return client

def init_collection(client: typesense.Client) -> None:
    video_transcription_schema = {
        "name": COLLECTION_NAME,
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "video_id", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "channel", "type": "string"},
            {"name": "upload_date", "type": "string"},
            {"name": "channel_follower_count", "type": "int32"},
            {"name": "view_count", "type": "int32"},
            {"name": "like_count", "type": "int32"},
            {"name": "start_time", "type": "int32"},
            {"name": "end_time", "type": "int32"},
            {"name": "content", "type": "string"},
        ],
        "default_sorting_field": "channel_follower_count",
    }
    init_collection_response = client.collections.create(video_transcription_schema)
    print(f"Initialized new collection: {init_collection_response}")

def sync_caption_data_to_collection(client: typesense.Client) -> None:
    """Index data from transcription files to typesense collection"""
    # Get all files from metadata directory
    metadata_dir = "metadata/"
    transcription_dir = "transcriptions/"
    metadata_json_filepaths = [os.path.join(metadata_dir, filename) for filename in sorted(os.listdir(metadata_dir))]
    transcription_filepaths = [os.path.join(transcription_dir, filename) for filename in sorted(os.listdir(transcription_dir))]

    metadata_filenames = [os.path.basename(filename).rsplit('.', maxsplit=1)[0].rsplit('.', maxsplit=1)[0] for filename in metadata_json_filepaths]
    transcription_filenames = [os.path.basename(filename).rsplit('.', maxsplit=1)[0] for filename in transcription_filepaths]
    print(
        f"Metadata but not in transcriptions: {len(metadata_filenames), len(transcription_filenames), set(metadata_filenames) - set(transcription_filenames)}"
    )
    # NOTE: When downloading playlists, the playlist metadata is downloaded as well. Thus, the # metadata files = # playlists + # transcriptions
    # We should just log this info, but not throw an error here.
    # assert len(metadata_json_filepaths) == len(transcription_filepaths), f"# metadata files: {len(metadata_json_filepaths)} is different from # transcription files: {len(transcription_filepaths)}. Something went wrong in the bash script to transcribe audio!"

    expected_num_docs = 0
    for transcription_filepath in transcription_filepaths:
        filename = os.path.basename(transcription_filepath).rsplit('.', maxsplit=1)[0]
        metadata_filepath = metadata_json_filepaths[
            metadata_json_filepaths.index(f"{os.path.join(metadata_dir, filename + '.info.json')}")
        ]
        # Parse metadata JSON
        with open(metadata_filepath, 'r') as fd:
            video_metadata = json.load(fd)
        # Parse transcription SRT files
        transcription_data = pysrt.open(transcription_filepath)
        # Create and upload to Typesense collection
        try:
            video_transcription_docs = [
                {
                    "id": f"{video_metadata['id']}_{sub_num}",
                    "video_id": video_metadata["id"],
                    "title": video_metadata["title"],
                    "channel": video_metadata["channel"],
                    "upload_date": video_metadata["upload_date"],
                    "channel_follower_count": video_metadata["channel_follower_count"],
                    "view_count": video_metadata["view_count"],
                    "like_count": video_metadata["like_count"],
                    "start_time": (sub.start.hours * 3600) + (sub.start.minutes * 60) + sub.start.seconds,
                    "end_time": (sub.end.hours * 3600) + (sub.end.minutes * 60) + sub.end.seconds,
                    "content": sub.text
                }
                for sub_num, sub in enumerate(transcription_data)
            ]
            expected_num_docs += len(video_transcription_docs)
        except KeyError as e:
            print(f"Could not find key {e} in metadata file {metadata_filepath}. Skipping this video.")
            continue

        # For some dumbass reason, the Typesense import endpoint always returns a HTTP 200 OK response, even if the import failed
        # So we have to manually check the response to see if it's successful: https://typesense.org/docs/0.22.2/api/documents.html#index-multiple-documents
        responses = typesense_client.collections[COLLECTION_NAME].documents.import_(
            video_transcription_docs, {"action": "upsert"}
        )
        for response in responses:
            if not response["success"]:
                print(f"Failed to index doc: {response}")

    num_docs = client.collections[COLLECTION_NAME].retrieve()['num_documents']
    print(f"Num docs in Typesense server: {num_docs}")
    # Only valid exception msg if collection is empty before running the script
    # assert expected_num_docs == actual_num_docs, f"Expected {expected_num_docs} documents, only inserted {actual_num_docs}"


if __name__ == "__main__":
    typesense_client = init_search_client()
    # typesense_client.collections[COLLECTION_NAME].delete()

    try:
        init_collection(typesense_client)
    except typesense.exceptions.ObjectAlreadyExists:
        pass

    sync_caption_data_to_collection(typesense_client)

    search_data = typesense_client.collections[COLLECTION_NAME].documents.search(
        {"q": "distributed", "query_by": "content", "sort_by": "start_time:asc", "page": 1, "per_page": 25}
    )
    print(f"Search data: {search_data, len(search_data['hits'])}")
    print(f"{search_data['found']} search results for distributed:")
    for doc_data in search_data['hits']:
        doc = doc_data['document']
        print(f"{doc['title']} : {doc['start_time']} - {doc['end_time']} : {doc['content']}")
