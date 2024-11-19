# Python Slim
FROM python:3.9-slim

WORKDIR /app

# Copy the app
COPY ./src .

# Install dependencies
RUN apt-get update && apt-get install -y \
  tesseract-ocr \
  tesseract-ocr-fra \
  libopencv-dev \
  python3-opencv \
  curl jq \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Download latest hero icons for use in template matching
RUN bash ./api/deadlockapi/heroes.sh

# Expose the port
CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
