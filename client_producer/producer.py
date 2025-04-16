import cv2
import base64
from kafka import KafkaProducer
import time


def encode_frame(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer)

cap = cv2.VideoCapture(0)
producer = None

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if producer is None:
        try:
            time.sleep(1)  
            producer = KafkaProducer(bootstrap_servers='localhost:9092')
        except Exception as e:
            print(f"Error connecting to Kafka: {e}")
    encoded_frame = encode_frame(frame)
    if producer is not None:
        producer.send('video-stream-raw', encoded_frame)
        producer.flush()
        time.sleep(0.05)

cap.release()
