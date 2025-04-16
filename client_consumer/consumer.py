import cv2
import base64
import numpy as np
from kafka import KafkaConsumer
import time

while True:
    time.sleep(1)  # Wait for Kafka to be ready
    consumer = KafkaConsumer(
        'video-stream-processed',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest'
    )
    

    for msg in consumer:
        print(f"msg: {msg}")
        jpg_original = base64.b64decode(msg.value)
        np_arr = np.frombuffer(jpg_original, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        cv2.imshow("Processed Video Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
