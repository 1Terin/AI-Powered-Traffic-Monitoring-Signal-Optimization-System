"""
YOLOv8 inference script using Ultralytics. Captures frames from RTSP (PTZ) cameras or local files,
runs detection, and optionally publishes detection summaries to MQTT.

Usage examples:
python ml/yolo_inference.py --source rtsp://user:pass@camera/stream --model yolov8n.pt --mqtt mqtt://mqtt --mqtt-topic detections
"""
import argparse
import json
import time

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

import cv2
import paho.mqtt.client as mqtt


def publish_mqtt(broker, topic, payload):
    client = mqtt.Client()
    # broker can be like mqtt://host or host:port. paho accepts host, so parse
    if broker.startswith('mqtt://'):
        broker_host = broker[len('mqtt://'):]
    else:
        broker_host = broker
    host = broker_host.split(':')[0]
    port = int(broker_host.split(':')[1]) if ':' in broker_host else 1883
    client.connect(host, port)
    client.publish(topic, json.dumps(payload))
    client.disconnect()


def run_detection(source, model_path, mqtt_broker=None, mqtt_topic=None, show=False):
    if YOLO is None:
        print('Ultralytics package not installed. Install with `pip install ultralytics`')
        return

    model = YOLO(model_path)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print('Failed to open source:', source)
        return

    frame_idx = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            frame_idx += 1
            # run inference on RGB
            results = model(frame, imgsz=640)
            detections = []
            # results is a Results object; iterate boxes
            for r in results:
                if r.boxes is None:
                    continue
                for box in r.boxes:
                    try:
                        xyxy = box.xyxy[0].cpu().numpy().tolist()
                        conf = float(box.conf[0].cpu().numpy()) if hasattr(box, 'conf') else float(box.conf[0])
                        cls = int(box.cls[0].cpu().numpy()) if hasattr(box, 'cls') else int(box.cls[0])
                    except Exception:
                        # fallback for different result types
                        xyxy = box.xyxy[0].tolist()
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                    detections.append({'bbox': xyxy, 'conf': conf, 'class': cls})

            summary = {
                'timestamp': int(time.time()),
                'frame': frame_idx,
                'detections': detections,
                'count': len(detections)
            }

            if mqtt_broker and mqtt_topic:
                try:
                    publish_mqtt(mqtt_broker, mqtt_topic, summary)
                except Exception as e:
                    print('MQTT publish failed', e)

            if show:
                # draw boxes
                for d in detections:
                    x1, y1, x2, y2 = map(int, d['bbox'][:4])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.imshow('YOLO', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='RTSP url or video file path')
    parser.add_argument('--model', default='yolov8n.pt', help='Path to YOLO model')
    parser.add_argument('--mqtt', default=None, help='MQTT broker url (e.g. mqtt://mqtt)')
    parser.add_argument('--mqtt-topic', default='sensors/camera/detections', help='MQTT topic to publish detections')
    parser.add_argument('--show', action='store_true', help='Show annotated frames')
    args = parser.parse_args()

    run_detection(args.source, args.model, mqtt_broker=args.mqtt, mqtt_topic=args.mqtt_topic, show=args.show)
