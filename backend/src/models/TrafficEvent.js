const mongoose = require('mongoose');

const trafficEventSchema = new mongoose.Schema({
  intersection: { type: String, required: true, default: 'intersection-1' },
  vehicleCount: { type: Number, default: 0 },
  averageSpeed: { type: Number, default: 0 },
  pollutionIndex: { type: Number, default: 0 },
  signalPhase: {
    type: String,
    enum: ['green', 'yellow', 'red'],
    default: 'green'
  },
  congestionLevel: {
    type: String,
    enum: ['low', 'moderate', 'high'],
    default: 'moderate'
  },
  sensorType: {
    type: String,
    enum: ['inductive_loop', 'radar', 'air_quality', 'camera', 'aggregated', 'unknown'],
    default: 'aggregated'
  },
  source: { type: String, default: 'mqtt' },
  timestamp: { type: Date, default: Date.now }
});

trafficEventSchema.index({ timestamp: -1 });
trafficEventSchema.index({ intersection: 1, timestamp: -1 });

module.exports = mongoose.model('TrafficEvent', trafficEventSchema);
