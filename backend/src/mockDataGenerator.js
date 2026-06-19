const intersections = ['A1', 'B2', 'C3', 'D4'];
const signalPhases = ['green', 'yellow', 'red'];
const congestionLevels = ['low', 'moderate', 'high'];

function randomBetween(min, max) {
  return Math.round(Math.random() * (max - min) + min);
}

function randomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

module.exports = function startMockTrafficStream(io, TrafficEvent) {
  setInterval(async () => {
    const event = new TrafficEvent({
      intersection: randomElement(intersections),
      vehicleCount: randomBetween(5, 45),
      averageSpeed: randomBetween(18, 65),
      pollutionIndex: randomBetween(30, 95),
      signalPhase: randomElement(signalPhases),
      congestionLevel: randomElement(congestionLevels),
      sensorType: 'aggregated',
      source: 'mock'
    });

    await event.save();
    io.emit('trafficUpdate', {
      id: event._id,
      timestamp: event.timestamp,
      intersection: event.intersection,
      vehicleCount: event.vehicleCount,
      averageSpeed: event.averageSpeed,
      pollutionIndex: event.pollutionIndex,
      signalPhase: event.signalPhase,
      congestionLevel: event.congestionLevel,
      sensorType: event.sensorType || 'aggregated',
      source: event.source || 'mock'
    });
  }, 5000);
};
