const mqtt = require('mqtt');

function startSimulators() {
  const brokerUrl = process.env.MQTT_BROKER || 'mqtt://mqtt';
  const client = mqtt.connect(brokerUrl);

  const intersections = ['A1', 'B2', 'C3', 'D4'];

  function rand(min, max) {
    return Math.round(Math.random() * (max - min) + min);
  }

  client.on('connect', () => {
    console.log('Sensor simulator connected to MQTT broker');

    setInterval(() => {
      const payload = {
        intersection: intersections[Math.floor(Math.random() * intersections.length)],
        vehicleCount: rand(0, 60),
        averageSpeed: rand(10, 80),
        pollutionIndex: rand(10, 200),
        signalPhase: ['green', 'yellow', 'red'][Math.floor(Math.random() * 3)],
        congestionLevel: ['low', 'moderate', 'high'][Math.floor(Math.random() * 3)]
      };

      client.publish('sensors/traffic/event', JSON.stringify(payload));
    }, 3000);
  });

  client.on('error', (err) => console.error('Simulator MQTT error:', err));

  return client;
}

module.exports = { startSimulators };
