# AI-Powered Traffic Monitoring & Signal Optimization System

This repository contains a scaffolded full-stack traffic monitoring system with:

- React frontend with real-time charts using Chart.js
- Express backend with Socket.IO for live updates
- MongoDB storage for traffic events and summaries
- Docker Compose infrastructure for local deployment

## Features

- REST API for traffic event ingestion and summaries
- WebSocket stream for real-time traffic dashboard updates
- Chart-based visualization of vehicle counts, speed, and pollution trends
- Simulation of sensor-generated traffic data

## Local development

1. Install dependencies for backend and frontend:
   - `npm run dev:backend`
   - `npm run dev:frontend`

2. Start infrastructure with Docker:
   - `npm run docker:up`

## Architecture

- `frontend/`: React + Vite dashboard
- `backend/`: Node.js + Express REST API + Socket.IO
- `docker-compose.yml`: MongoDB, backend, frontend

Additional components added:

- MQTT bridge and sensor simulators: `backend/src/mqttBridge.js`, `backend/src/sensorSimulators.js`
- PostgreSQL optional support: `backend/src/postgresClient.js` and `docker-compose.yml` service `postgres`
- Dataset import helper: `data_import/import_datasets.py`
- ML starter scripts: `ml/lstm_train.py`, `ml/yolo_inference.py`, `ml/rl_signal_opt.py`
- Kubernetes manifests: `k8s/`

Quick run (local with Docker):

```bash
# start services (Mongo, Postgres, MQTT, backend, frontend)
npm run docker:up

# to enable simulated sensors, set env var before starting backend (if running directly):
setx SIMULATE_SENSORS 1
cd backend && npm run dev
```

ML notes:

- Use `python data_import/import_datasets.py` to verify datasets are available under `data_import/datasets/`.
- `ml/lstm_train.py` is a starter script for time-series forecasting (requires TensorFlow).
- `ml/yolo_inference.py` is a placeholder for integrating a YOLO runtime.


## Dataset References

- Smart Traffic Management Dataset: https://www.kaggle.com/datasets/smmmmmmmmmmmm/smart-traffic-management-dataset
- Real Environment Vehicle Images: https://www.kaggle.com/datasets/hanif535/real-environment-vehicle-images
- Smart Traffic Monitoring Dataset: https://www.kaggle.com/datasets/programmer3/smart-traffic-monitoring-dataset
- Perception-Based Adaptive Traffic Management Dataset: https://rosap.ntl.bts.gov/view/dot/84510
