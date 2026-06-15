const http = require('http');
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const { Server } = require('socket.io');
const TrafficEvent = require('./src/models/TrafficEvent');
const startMockTrafficStream = require('./src/mockDataGenerator');
const startMqttBridge = require('./src/mqttBridge');
const { startSimulators } = require('./src/sensorSimulators');
const { initPostgres } = require('./src/postgresClient');

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 4000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://mongo:27017/trafficdb';

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

app.get('/api/traffic', async (req, res) => {
  const events = await TrafficEvent.find().sort({ timestamp: -1 }).limit(100);
  res.json(events);
});

app.get('/api/traffic/summary', async (req, res) => {
  const summary = await TrafficEvent.aggregate([
    { $sort: { timestamp: -1 } },
    { $limit: 50 },
    {
      $group: {
        _id: null,
        averageSpeed: { $avg: '$averageSpeed' },
        averagePollution: { $avg: '$pollutionIndex' },
        totalVehicles: { $sum: '$vehicleCount' }
      }
    }
  ]);

  res.json(summary[0] || { averageSpeed: 0, averagePollution: 0, totalVehicles: 0 });
});

app.post('/api/traffic', async (req, res) => {
  const payload = req.body;
  const event = new TrafficEvent({
    intersection: payload.intersection || 'intersection-1',
    vehicleCount: payload.vehicleCount || 0,
    averageSpeed: payload.averageSpeed || 0,
    pollutionIndex: payload.pollutionIndex || 0,
    signalPhase: payload.signalPhase || 'green',
    congestionLevel: payload.congestionLevel || 'moderate'
  });

  await event.save();
  io.emit('trafficUpdate', event);
  res.status(201).json(event);
});

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

async function start() {
  await mongoose.connect(MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
  });

  server.listen(PORT, () => {
    console.log(`Backend running on http://localhost:${PORT}`);
  });

  // start existing mock stream saving to MongoDB + Socket.IO
  startMockTrafficStream(io, TrafficEvent);

  // start MQTT bridge to accept sensor data via MQTT and publish to Socket.IO
  try {
    startMqttBridge(io, TrafficEvent);
  } catch (err) {
    console.warn('MQTT bridge failed to start', err.message || err);
  }

  // optionally run local sensor simulators (publishes MQTT messages)
  if (process.env.SIMULATE_SENSORS === '1') {
    startSimulators();
  }

  // initialize Postgres connection (optional)
  try {
    const { sequelize } = initPostgres();
    sequelize.authenticate().then(() => console.log('Postgres connected')).catch(() => {});
  } catch (err) {
    // ignore if not configured
  }
}

start().catch((error) => {
  console.error('Startup error:', error);
  process.exit(1);
});
