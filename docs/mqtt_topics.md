# MQTT Topics and Schemas

This document describes the MQTT topics used by the system, message formats, and connection/security guidance.

## Topics

- `sensors/traffic/event`
  - Purpose: Raw sensor messages from edge devices (loops, radars, air-quality sensors)
  - Example payload (JSON):
    ```json
    {
      "intersection": "A1",
      "vehicleCount": 12,
      "averageSpeed": 45.2,
      "pollutionIndex": 42.5,
      "signalPhase": "green",
      "congestionLevel": "moderate",
      "timestamp": 1620000000
    }
    ```

- `sensors/camera/detections`
  - Purpose: Camera object detections (YOLO output)
  - Example payload:
    ```json
    {
      "timestamp": 1620000000,
      "cameraId": "PTZ-1",
      "frame": 123,
      "count": 3,
      "detections": [
        {"bbox": [x1,y1,x2,y2], "conf": 0.92, "class": 2},
        {"bbox": [..], "conf": 0.88, "class": 2}
      ]
    }
    ```

- `control/signals/commands`
  - Purpose: Commands to change traffic signal phases (used by RL or operators)
  - Example payload:
    ```json
    {
      "intersection": "A1",
      "action": "set_phase",
      "phase": "green",
      "duration": 30
    }
    ```

## Security and Connection

- Use TLS (MQTT over 8883) to encrypt traffic. The test mosquitto config supports TLS in `mosquitto/config`.
- Use username/password stored in the Mosquitto `passwords` file or use JWT tokens as the password if configured.
- Devices should authenticate and register with the backend to receive tokens and metadata:
  - `POST /api/devices/register` with JSON `{ "deviceId": "DEVICE123" }` returns `{ deviceId, secret, token }`.
  - Use the returned `token` as a bearer token for REST APIs, or as the MQTT password when connecting.

## QoS and Retained Messages

- Sensor telemetry: QoS 0 or 1 depending on network reliability.
- Important commands and state: consider QoS 1 and retained messages for last-known-state.

## Schema Evolution

- Use `type` or `schemaVersion` fields in messages to allow parsers to handle changes.
- Keep messages small and send full snapshots only when necessary.
