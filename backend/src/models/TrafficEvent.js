const mongoose = require('mongoose');

const trafficEventSchema = new mongoose.Schema({
  timestamp: {
    type: Date,
    default: () => new Date()
  },
  intersection: {
    type: String,
    required: true,
    default: 'intersection-1'
  },
  vehicleCount: {
    type: Number,
    required: true,
    default: 0
  },
  averageSpeed: {
    type: Number,
    required: true,
    default: 0
  },
  pollutionIndex: {
    type: Number,
    required: true,
    default: 0
  },
  signalPhase: {
    type: String,
    required: true,
    enum: ['green', 'yellow', 'red'],
    default: 'green'
  },
  congestionLevel: {
    type: String,
    required: true,
    enum: ['low', 'moderate', 'high'],
    default: 'moderate'
  }
});

module.exports = mongoose.model('TrafficEvent', trafficEventSchema);
