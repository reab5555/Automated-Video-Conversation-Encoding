# Automated Video Conversion and Encoding Pipeline

This project provides an automated solution for video conversion and encoding. It is designed to run on Kubernetes, leveraging Google Cloud Storage (GCS) for managing input and output files. The pipeline includes an automated scheduling mechanism to process videos at regular intervals.

## Features

- **Video Conversion and Encoding**:
  - Converts videos to `H.265` codec for high compression and quality.
  - Dynamically adjusts bitrate based on video resolution (e.g., `10M` for 1080p and above, `5M` for lower resolutions).
  - Outputs videos scaled to a maximum resolution of 1080p.

- **Cloud Integration**:
  - Fetches input video files from a specified GCS bucket directory.
  - Uploads processed video files to another directory in the same or different GCS bucket.
  - Maintains metadata of processed files to avoid reprocessing.

- **Kubernetes Deployment**:
  - Runs as a Kubernetes job for scalable and isolated video processing tasks.
  - Configurable through a Kubernetes YAML manifest file (`job.yaml`).

- **Scheduling**:
  - Automated scheduling through Kubernetes CronJobs or an external scheduler.

- **Cross-Platform Support**:
  - Compatible with Linux and Windows for local development and debugging.

## How It Works

1. **Input Videos**:
   - The pipeline scans a GCS bucket directory for new video files (e.g., `.mp4`, `.avi`, `.mov`, `.mkv`).
   - Processes only unprocessed files.

2. **Processing**:
   - Downloads videos locally from GCS.
   - Encodes videos using FFmpeg.
   - Tracks progress using a command-line progress bar.
   - Cleans up local temporary files after processing.

3. **Output**:
   - Uploads the processed video to the specified output directory in the GCS bucket.
   - Saves metadata of processed files to a metadata directory in GCS.

## File Overview

### `video_converter.py`

- The main script to handle:
  - Video downloading from GCS.
  - Video conversion and encoding.
  - Uploading the processed videos to GCS.
  - Managing metadata of processed files.

### `build_and_push_linux.sh`

- Bash script for building and pushing the Docker image for the pipeline to a container registry.

### `build_and_push_win.bat`

- Batch script for building and pushing the Docker image on Windows systems.

### `Dockerfile`

- Dockerfile to containerize the video processing application:
  - Installs FFmpeg and necessary dependencies.
  - Includes the Python application and configurations.

### `job.yaml`

- Kubernetes Job manifest file to define:
  - The container image for the pipeline.
  - Environment variables for GCS configuration (e.g., bucket names, prefixes).
  - Resource allocation for video processing tasks.

## Prerequisites

1. **Google Cloud Platform**:
   - A GCS bucket for input and output files.
   - Service account with appropriate permissions (`roles/storage.objectAdmin`).

2. **Kubernetes**:
   - A Kubernetes cluster to deploy the job.
   - Kubernetes CLI (`kubectl`) configured to access the cluster.

3. **Docker**:
   - Docker installed for building container images.

4. **FFmpeg**:
   - Pre-installed in the Docker container for video processing.

## Setup and Deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
