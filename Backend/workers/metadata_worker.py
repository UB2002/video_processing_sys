# workers/metadata_worker.py
import pika
import json
import cv2
import os
import requests
from app.config import STORAGE_DIR, RABBITMQ_HOST, EXCHANGE_NAME

def extract_metadata(filename):
    video_path = os.path.join(STORAGE_DIR, filename)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    
    if fps > 0:
        duration = frame_count / fps
    else:
        duration = None  # or handle it in another appropriate way
    
    metadata = {
        "filename": filename,
        "duration": duration,
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": fps,
    }
    cap.release()
    return metadata

def callback(ch, method, properties, body):
    data = json.loads(body)
    filename = data["filename"]
    client_id = data.get("client_id", "default_client")
    
    metadata = extract_metadata(filename)
    print(f"Extracted Metadata: {metadata}")

    # Send metadata update to FastAPI internal endpoint
    response = requests.post(
        "http://localhost:8000/internal/metadata-extraction-status",
        json={"client_id": client_id, "metadata": metadata}
    )
    print(f"Metadata sent to API: {response.status_code}")

# Setup RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

# Declare the exchange
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')

# Create a queue with a random name
result = channel.queue_declare(queue="metadata_extraction", exclusive=False)
queue_name = result.method.queue

# Bind the queue to the exchange
channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

# Set up consumption
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Metadata Extraction Worker Started...")
channel.start_consuming()