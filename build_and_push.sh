#!/bin/bash

# Default values
PROJECT_ID=${1:-"project-id"}
REGION=${2:-"region"}
REPO_NAME=${3:-"arifact_registry_repo"}
IMAGE_NAME=${4:-"video-converter"}
TAG=${5:-"v1"}

# Build the Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

# Tag the Docker image
echo "Tagging Docker image..."
docker tag ${IMAGE_NAME} ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}

# Authenticate with Artifact Registry
echo "Authenticating with Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Push the image
echo "Pushing Docker image..."
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}

echo "Docker image pushed successfully!"
