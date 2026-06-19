const mqtt = require('mqtt');

const INTERSECTIONS = ['A1', 'B2', 'C3', 'D4'];
const SIGNAL_PHASES = ['green', 'yellow', 'red'];
const CONGESTION_LEVELS = ['low', 'moderate', 'high'];

function rand(min, max) {
  return Math.round(Math.random() * (max - min) + min);
}

function randomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function startSimulators() {
  const brokerUrl = process.env.MQTT_BROKER || 'mqtt://mqtt';
  const client = mqtt.connect(brokerUrl);

  client.on('connect', () => {
    console.log('Sensor simulators connected to MQTT broker');

    // Inductive loop sensors — vehicle presence/count at stop lines
    setInterval(() => {
      const intersection = randomElement(INTERSECTIONS);
      client.publish(
        'sensors/inductive/event',
        JSON.stringify({
          intersection,
          sensorType: 'inductive_loop',
          vehicleCount: rand(0, 45),
          timestamp: Date.now()
        })
      );
    }, 2500);

    // Radar sensors — vehicle speed monitoring
    setInterval(() => {
      const intersection = randomElement(INTERSECTIONS);
      client.publish(
        'sensors/radar/event',
        JSON.stringify({
          intersection,
          sensorType: 'radar',
          averageSpeed: rand(15, 85),
          timestamp: Date.now()
        })
      );
    }, 3000);

    // Air quality sensors — pollution index
    setInterval(() => {
      const intersection = randomElement(INTERSECTIONS);
      client.publish(
        'sensors/airquality/event',
        JSON.stringify({
          intersection,
          sensorType: 'air_quality',
          pollutionIndex: rand(20, 180),
          timestamp: Date.now()
        })
      );
    }, 4000);

    // Aggregated traffic event (loops + radar + air quality combined)
    setInterval(() => {
      const intersection = randomElement(INTERSECTIONS);
      const signalPhase = randomElement(SIGNAL_PHASES);
      const payload = {
        intersection,
        sensorType: 'aggregated',
        vehicleCount: rand(5, 55),
        averageSpeed: rand(18, 72),
        pollutionIndex: rand(25, 120),
        signalPhase,
        congestionLevel: randomElement(CONGESTION_LEVELS),
        timestamp: Date.now()
      };
      client.publish('sensors/traffic/event', JSON.stringify(payload));
    }, 3500);
  });

  client.on('error', (err) => console.error('Simulator MQTT error:', err));

  return client;
}

module.exports = { startSimulators };
