"""YOLO inference placeholder: publishes periodic detection stubs to MQTT.
This service simulates camera detections and keeps running to support the live stack.
"""
import argparse
import time
import json
import random

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


def publish_mqtt(broker, topic, payload):
    if mqtt is None:
        print('MQTT library not installed; falling back to stdout publish')
        print('PUB', topic, json.dumps(payload))
        return

    client = mqtt.Client()
    if broker.startswith('mqtt://'):
        broker_host = broker[len('mqtt://'):]
    else:
        broker_host = broker
    host = broker_host.split(':')[0]
    port = int(broker_host.split(':')[1]) if ':' in broker_host else 1883
    client.connect(host, port)
    client.publish(topic, json.dumps(payload))
    client.disconnect()


def run_stub(mqtt_url, topic, interval=3):
    frame = 0
    while True:
        count = random.randint(1, 8)
        det = {
            'timestamp': int(time.time()),
            'cameraId': 'PTZ-1',
            'intersection': random.choice(['A1', 'B2', 'C3', 'D4']),
            'frame': frame,
            'detections': [
                {
                    'class': random.choice(['car', 'truck', 'bus', 'motorcycle']),
                    'confidence': round(random.uniform(0.6, 0.99), 2),
                    'bbox': [10 + i * 20, 20, 150 + i * 20, 120]
                }
                for i in range(count)
            ],
            'count': count
        }
        publish_mqtt(mqtt_url, topic, det)
        frame += 1
        time.sleep(interval)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mqtt', default='mqtt://mqtt:1883')
    p.add_argument('--topic', default='sensors/camera/detections')
    p.add_argument('--interval', type=int, default=3)
    args = p.parse_args()
    print('Starting YOLO stub publishing to', args.mqtt, 'topic', args.topic)
    run_stub(args.mqtt, args.topic, interval=args.interval)


if __name__ == '__main__':
    main()
