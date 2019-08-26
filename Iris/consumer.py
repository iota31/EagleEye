from kafka import KafkaConsumer
from time import sleep
import json

KAFKA_BROKER_URL = "198.245.53.163:9092"

KAFKA_TOPIC = "eagle-eye"

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    while True:
        for message in consumer:
            print(message.value)
            sleep(0.2)

if __name__ == "__main__":
    main()
