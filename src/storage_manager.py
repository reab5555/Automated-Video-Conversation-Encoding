from google.cloud import storage
import json
import os
from datetime import datetime


class StorageManager:
    def __init__(self, bucket_name):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def list_videos(self, prefix):
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
        return [
            blob.name for blob in self.bucket.list_blobs(prefix=prefix)
            if blob.name.lower().endswith(video_extensions)
        ]

    def download_video(self, source_blob_name, destination):
        print(f"Downloading: {source_blob_name}")
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination)

    def upload_video(self, source, destination_blob_name):
        print(f"Uploading to: {destination_blob_name}")
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source)

    def get_processed_files(self, metadata_prefix):
        try:
            blob = self.bucket.blob(f"{metadata_prefix}processed_files.json")
            return json.loads(blob.download_as_string())
        except Exception:
            return {}

    def save_metadata(self, metadata, path):
        blob = self.bucket.blob(path)
        blob.upload_from_string(json.dumps(metadata, indent=2))

    def update_processed_files(self, video_path, info, metadata_prefix):
        lock_blob = self.bucket.blob(f"{metadata_prefix}update.lock")

        try:
            lock_blob.upload_from_string('locked', if_generation_match=0)

            processed_files = self.get_processed_files(metadata_prefix)
            processed_files[video_path] = info

            self.save_metadata(processed_files, f"{metadata_prefix}processed_files.json")

        finally:
            try:
                lock_blob.delete()
            except Exception:
                pass