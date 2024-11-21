# Automated Video Conversion and Encoding Pipeline

This project provides an automated solution for video conversion and encoding. It is designed to run on Kubernetes, leveraging Google Cloud Storage (GCS) for managing input and output files. The pipeline includes an automated scheduling mechanism to process videos at regular intervals.

## Features

- **Video Conversion and Encoding**:
  - Converts videos to `H.265` codec for high compression and quality.
  - Dynamically adjusts bitrate based on video resolution.
  - Outputs videos scaled to a resolution of 1080p.

- **Cloud Integration**:
  - Fetches the latest input video files from a specified GCS bucket directory.
  - Uploads/export processed video files to an output directory in the same GCS bucket.
  - Maintains metadata of processed files to avoid reprocessing.

- **Kubernetes Deployment**:
  - Runs as a Kubernetes job for scalable and isolated video processing tasks.
  - Configurable through a Kubernetes YAML manifest file (`job.yaml`).

- **Scheduling**:
  - Automated scheduling through Kubernetes CronJob (24-hours interval).

- **Cross-Platform Support**:
  - Compatible with Linux and Windows.

## Workflow

1. **Input Videos**:
   - The pipeline scans a GCS bucket directory for new video files (e.g., `.mp4`, `.avi`, `.mov`, `.mkv`).
   - Processes only unprocessed files.

2. **Processing**:
   - Fetch videos from GCS bucket input directory.
   - Encodes videos using FFmpeg.
   - Tracks progress using a command-line progress bar (or in Kubernetes/GCP log monitoring).
   - Cleans up local temporary files after processing.

3. **Output**:
   - Uploads/export the processed video to the specified output directory in the GCS bucket.
   - Saves metadata of processed files to a metadata directory in GCS.

## File Overview

### `video_converter.py`

- The main script to handle:
  - Video fetching from GCS.
  - Video conversion and encoding.
  - Uploading/exporting the processed videos to GCS.
  - Managing metadata of processed files.

### Option 1: `build_and_push_linux.sh`

- Bash script for building and pushing the Docker image for the pipeline to a container registry (linux).

### Option 2: `build_and_push_win.bat`

- Batch script for building and pushing the Docker image on Windows systems.

### `Dockerfile`

- Dockerfile to containerize the video processing application:
  - Installs FFmpeg and necessary dependencies.
  - Includes the Python application and configurations.

### `job.yaml`

- Kubernetes Job yaml file to define:
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
```

### 2. Configure Environment Variables

Set the following environment variables:
```bash
    BUCKET_NAME: Name of the GCS bucket.
    INPUT_PREFIX: Input directory in the GCS bucket.
    OUTPUT_PREFIX: Output directory in the GCS bucket.
```

### 3. Build and Push Docker Image
On Linux:

```bash
./build_and_push_linux.sh
```

On Windows:
```bash
build_and_push_win.bat
```

### 4. Deploy on Kubernetes

Modify the job.yaml file to include your Docker image and environment variables.  
Deploy the job using kubectl:

kubectl apply -f job.yaml

### 5. Schedule the Job (Optional)

    Use Kubernetes CronJobs to schedule the job at regular intervals.
