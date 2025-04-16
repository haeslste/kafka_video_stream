from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
import cv2
import numpy as np
import base64

spark = SparkSession \
    .builder \
    .appName("KafkaStreamProcessor") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Kafka configuration
raw_topic = "video-stream-raw"
processed_topic = "video-stream-processed"
kafka_bootstrap = "kafka:9092"

# UDF to process frames
def detect_lines(encoded_frame):
    jpg_original = base64.b64decode(encoded_frame)
    np_arr = np.frombuffer(jpg_original, dtype=np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)

    if lines is not None:
        for line in lines:
            x1,y1,x2,y2 = line[0]
            cv2.line(frame,(x1,y1),(x2,y2),(0,255,0),2)

    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode()

process_udf = udf(detect_lines, StringType())

# Kafka stream read
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap) \
    .option("subscribe", raw_topic) \
    .option("startingOffsets", "latest") \
    .load()

frames = raw_stream.selectExpr("CAST(value AS STRING)")

processed_frames = frames.withColumn("value", process_udf(col("value")))

query = processed_frames.selectExpr("CAST(value AS STRING)") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap) \
    .option("topic", processed_topic) \
    .option("checkpointLocation", "/tmp/spark-checkpoints") \
    .start()

query.awaitTermination()
