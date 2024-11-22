import os
import uuid
import shutil
from datetime import datetime
from tqdm import tqdm
from src.video_processor import VideoProcessor
from src.storage_manager import StorageManager
from src.logger import ProcessingLogger


def setup_temp_dir():
    temp_dir = f'/tmp/video_processing_{uuid.uuid4().hex[:8]}'
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

# Fetch the next unprocessed file.
def get_next_file_to_process(storage, input_prefix, metadata_prefix):
    all_videos = storage.list_videos(input_prefix)
    processed_files = storage.get_processed_files(metadata_prefix)

    for video in all_videos:
        # Skip already processed or in-progress files
        if video not in processed_files:
            try:
                # Mark this file as being processed
                storage.update_processed_files(video, {"status": "processing"}, metadata_prefix)
                return video
            except Exception as e:
                print(f"Failed to lock file {video}: {e}")
                continue

    return None


def process_video(video_path, storage, processor, logger, input_prefix, output_prefix, metadata_prefix):
    temp_dir = setup_temp_dir()
    input_path = os.path.join(temp_dir, 'input.mp4')
    output_path = os.path.join(temp_dir, 'output.mp4')

    start_time = datetime.now()
    try:
        # Download
        print(f"\nDownloading: {video_path}")
        storage.download_video(video_path, input_path)

        # Convert
        print("Converting video...")
        results = processor.convert_video(input_path, output_path)

        # Upload
        current_date = datetime.now().strftime('%Y-%m-%d')
        output_name = f"{os.path.splitext(os.path.basename(video_path))[0]}_{uuid.uuid4().hex[:8]}.mp4"
        dest_path = f"{output_prefix}{current_date}/{output_name}"

        print("Uploading converted video...")
        storage.upload_video(output_path, dest_path)

        # Update metadata
        metadata = {
            'processed_date': current_date,
            'output_path': dest_path,
            'success': True,
            'processing_results': results
        }
        storage.update_processed_files(video_path, metadata, metadata_prefix)

        # Log success
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.log_conversion(video_path, True, processing_time, results)
        print(f"✓ Success: {video_path}")
        return True

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.log_conversion(video_path, False, processing_time, error=str(e))
        print(f"Error processing {video_path}: {e}")
        return False

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    # Configuration
    bucket_name = os.getenv('BUCKET_NAME', 'main_il')
    input_prefix = os.getenv('INPUT_PREFIX', 'video_conversion_workplace/input_directory/')
    output_prefix = os.getenv('OUTPUT_PREFIX', 'video_conversion_workplace/output_directory/')
    metadata_prefix = os.getenv('METADATA_PREFIX', 'video_conversion_workplace/metadata/')

    print("\nVideo Converter starting...")
    print(f"Bucket: {bucket_name}")
    print(f"Input prefix: {input_prefix}")
    print(f"Output prefix: {output_prefix}")

    # Initialize components
    storage = StorageManager(bucket_name)
    processor = VideoProcessor()
    logger = ProcessingLogger(storage, metadata_prefix)

    # Get all videos
    all_videos = storage.list_videos(input_prefix)
    total_videos = len(all_videos)
    processed_videos = 0

    print(f"Found {total_videos} videos to process.")

    # Progress bar
    with tqdm(total=total_videos, desc="Processing Files", unit="file") as pbar:
        while True:
            # Get the next video to process
            video_path = get_next_file_to_process(storage, input_prefix, metadata_prefix)

            if not video_path:
                print("No videos left to process. Exiting...")
                break

            print(f"\nProcessing video: {video_path}")
            if process_video(
                video_path, storage, processor, logger,
                input_prefix, output_prefix, metadata_prefix
            ):
                processed_videos += 1
                pbar.update(1)

    print(f"\nProcessed {processed_videos}/{total_videos} videos.")


if __name__ == "__main__":
    start_time = datetime.now()
    try:
        main()
    finally:
        duration = datetime.now() - start_time
        print(f"\nTotal runtime: {duration}")
