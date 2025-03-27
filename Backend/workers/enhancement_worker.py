# workers/enhancement_worker.py
import pika
import json
import cv2
import os
import requests
from app.config import STORAGE_DIR, RABBITMQ_HOST, EXCHANGE_NAME


def enhance_video(filename):
    input_path = os.path.join(STORAGE_DIR, filename)
    output_path = os.path.join(STORAGE_DIR, f"enhanced_{filename}")
    
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(
        output_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
        (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    )
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=30)  # Brightness increase
        out.write(frame)
    
    cap.release()
    out.release()
    return output_path

def callback(ch, method, properties, body):
    data = json.loads(body)
    filename = data["filename"]
    client_id = data.get("client_id", "default_client")
    
    enhanced_path = enhance_video(filename)
    print(f"Enhanced video saved: {enhanced_path}")

    # Send enhancement status update to FastAPI internal endpoint
    response = requests.post(
        "http://localhost:8000/internal/video-enhancement-status",
        json={"client_id": client_id, "filename": f"enhanced_{filename}"}
    )
    print(f"Enhancement status sent to API: {response.status_code}")

# Setup RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

# Declare the exchange
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')

# Create a queue with a random name
result = channel.queue_declare(queue="video_enhancement", exclusive=False)
queue_name = result.method.queue

# Bind the queue to the exchange
channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

# Set up consumption
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Video Enhancement Worker Started...")
channel.start_consuming()