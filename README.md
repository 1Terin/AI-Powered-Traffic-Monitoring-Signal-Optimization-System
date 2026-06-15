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

## Dataset References

- Smart Traffic Management Dataset: https://www.kaggle.com/datasets/smmmmmmmmmmmm/smart-traffic-management-dataset
- Real Environment Vehicle Images: https://www.kaggle.com/datasets/hanif535/real-environment-vehicle-images
- Smart Traffic Monitoring Dataset: https://www.kaggle.com/datasets/programmer3/smart-traffic-monitoring-dataset
- Perception-Based Adaptive Traffic Management Dataset: https://rosap.ntl.bts.gov/view/dot/84510
