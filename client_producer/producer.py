import cv2
import base64
from kafka import KafkaProducer
import time

producer = KafkaProducer(bootstrap_servers='localhost:9092')

def encode_frame(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    encoded_frame = encode_frame(frame)
    producer.send('video-stream-raw', encoded_frame)
    producer.flush()
    time.sleep(0.05)

cap.release()
