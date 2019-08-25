from kafka import KafkaProducer
from time import sleep
import json
import push_to_db

KAFKA_BROKER_URL = "198.245.53.163:9092"

KAFKA_TOPIC = "eagle-eye"

def get_data(DATABASE):
    db = push_to_db.Db(DATABASE)
    return db.select()

def main(DATABASE):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda value: json.dumps(value).encode()
    )

    while True:
        data = get_data(DATABASE)
        producer.send(KAFKA_TOPIC, value=data)
        print(data)
        sleep(10)

if __name__ == "__main__":
    main()