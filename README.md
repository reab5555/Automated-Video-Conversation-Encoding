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
  
5. **Google Artifact Registry**:
   - A Google Artifact Registry to store and manage the container image.

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

### 4. Configure GCP Service Accounts and Permissions
```bash
# Create service accounts
gcloud iam service-accounts create gke-video-converter
gcloud iam service-accounts create art-registry-sa

# Grant storage permissions
gcloud projects add-iam-policy-binding [PROJECT_ID] \
    --member="serviceAccount:gke-video-converter@[PROJECT_ID].iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Grant Artifact Registry permissions
gcloud artifacts repositories add-iam-policy-binding [REPOSITORY_NAME] \
    --location=[REGION] \
    --member="serviceAccount:art-registry-sa@[PROJECT_ID].iam.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"

# Enable Workload Identity
gcloud container clusters update [CLUSTER_NAME] \
    --workload-pool=[PROJECT_ID].svc.id.goog \
    --location=[REGION]

# Create Kubernetes service account
kubectl create serviceaccount art-registry-sa

# Bind service accounts
gcloud iam service-accounts add-iam-policy-binding \
    art-registry-sa@[PROJECT_ID].iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:[PROJECT_ID].svc.id.goog[default/art-registry-sa]"

```
    
### 5. Deploy on Kubernetes

Modify the job.yaml file to include your Docker image and environment variables.  
Deploy the job using kubectl:
```bash
kubectl apply -f job.yaml
```
