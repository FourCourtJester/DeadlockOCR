# Use Python 3.9 base image
FROM python:3.9-slim

# Define the default user as vscode (important for VSCode devcontainers)
USER $USER

# Install dependencies
RUN apt-get update && apt-get install -y \
  tesseract-ocr \
  tesseract-ocr-fra \
  libopencv-dev \
  python3-opencv \
  # Install additional utilities
  git curl wget jq \
  && apt-get clean

# Install Python packages (move to requirements.txt if you want more control)
RUN pip install flask flask-cors pytesseract opencv-python-headless numpy

# Create app directory
WORKDIR /workspace

COPY . .