from kafka import KafkaProducer
from time import sleep
import json
import push_to_db

KAFKA_BROKER_URL = "198.245.53.163:9092"

KAFKA_TOPIC = "eagle-eye"

def get_data(DATABASE):
    db = push_to_db.Db(DATABASE)
    return db.select()

def Convert(tup):
    di = {}
    for a, b in tup:
        di.setdefault(a, []).append(b)
    return di

def main(DATABASE):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda value: json.dumps(value).encode()
    )

    while True:
        data = get_data(DATABASE)
        print("Data: ",data)
        _dict = Convert(data)
        print("Dict:", _dict)
        producer.send(KAFKA_TOPIC, value=_dict)
        sleep(10)

#if __name__ == "__main__":
#    main()
