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

1. Install dependencies and run locally:
   - `npm run dev:backend`
   - `npm run dev:frontend`

2. Start the app stack with Docker Compose:
   - `docker compose up -d mongo mqtt inference backend frontend yolo`
   - `docker compose down`

3. Start monitoring services (optional):
   - `docker compose up -d prometheus grafana`

## Local URLs

- Frontend dashboard: `http://localhost:4173/`
- Backend health: `http://localhost:4000/api/health`
- Inference health: `http://localhost:5001/health`
- Prometheus: `http://localhost:9090` (optional)
- Grafana: `http://localhost:3000` (optional)

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
# start services (Mongo, Postgres, MQTT, backend, frontend, inference) (no logs)
docker compose up -d mongo mqtt inference backend frontend yolo

# for everything (including logs)
npm run docker:up

# stop the app stack
docker compose down
```

Then open the dashboard at:

- `http://localhost:4173/`

Optional monitoring:
```bash
docker compose up -d prometheus grafana
```

To enable simulated sensors when running backend locally:
```powershell
setx SIMULATE_SENSORS 1
cd backend && npm run dev
```

ML notes:

- Use `python data_import/import_datasets.py` to verify datasets are available under `data_import/datasets/`.
- `ml/lstm_train.py` is a starter script for time-series forecasting (requires TensorFlow).
- `ml/yolo_inference.py` is a placeholder for integrating a YOLO runtime.

Extended ML & Ops notes:

- YOLO inference: use `ml/yolo_inference.py`. Install dependencies from `ml/requirements-ml.txt` and run:

```bash
python ml/yolo_inference.py --source rtsp://<camera> --model yolov8n.pt --mqtt mqtt://localhost:1883 --show
```

- LSTM training: improved trainer at `ml/lstm_train.py`. Example:

```bash
python ml/lstm_train.py --data data_import/datasets/smart_traffic_management.csv --seq-len 12 --epochs 20
```

- Reinforcement Learning: train a PPO agent with `ml/train_rl.py`:

```bash
python ml/train_rl.py --timesteps 50000
```

- Monitoring: Prometheus is available at `http://localhost:9090` and Grafana at `http://localhost:3000` when running `docker compose up -d prometheus grafana`.
- Local stack: use `docker compose up -d backend frontend inference` to start the app, inference API, and backend together.

Forecast panel and inference API

- A simple forecast panel in the dashboard can display LSTM predictions for short-term vehicle counts.
- A lightweight Flask inference server is provided at `ml/infer_api.py`. It will load a Keras `.h5` model if present at `ml/lstm_traffic_model.h5` and expose a `/predict` endpoint (POST) that accepts JSON `{"window": [v1, v2, ...]}` and returns `{"prediction": <float>}`.

To run the inference API locally:

```bash
python -m pip install -r ml/requirements-ml.txt
python ml/infer_api.py
```

Notes:
- If no trained model is present, the inference server returns a simple fallback (last observed value) so the dashboard still shows a forecast value.
- The frontend calls `http://localhost:5001/predict` by default; ensure the inference server is running and reachable when using the forecast panel.


## Dataset References

- Smart Traffic Management Dataset: https://www.kaggle.com/datasets/smmmmmmmmmmmm/smart-traffic-management-dataset
- Real Environment Vehicle Images: https://www.kaggle.com/datasets/hanif535/real-environment-vehicle-images
- Smart Traffic Monitoring Dataset: https://www.kaggle.com/datasets/programmer3/smart-traffic-monitoring-dataset
- Perception-Based Adaptive Traffic Management Dataset: https://rosap.ntl.bts.gov/view/dot/84510
