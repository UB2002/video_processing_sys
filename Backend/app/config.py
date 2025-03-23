import os

# Directory to store uploaded and processed videos
STORAGE_DIR = "storage"

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "video_tasks"

# Ensure the storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)