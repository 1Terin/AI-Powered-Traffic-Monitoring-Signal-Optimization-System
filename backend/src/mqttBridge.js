const mqtt = require('mqtt');

function startMqttBridge(io, TrafficEvent) {
  const brokerUrl = process.env.MQTT_BROKER || 'mqtt://mqtt';
  const client = mqtt.connect(brokerUrl);

  client.on('connect', () => {
    console.log('Connected to MQTT broker at', brokerUrl);
    // subscribe to common sensor topics
    client.subscribe('sensors/+/event', (err) => {
      if (err) console.error('MQTT subscribe error', err);
    });
  });

  client.on('message', async (topic, msg) => {
    try {
      const payload = JSON.parse(msg.toString());
      // normalize payload
      const event = new TrafficEvent({
        intersection: payload.intersection || 'simulated',
        vehicleCount: payload.vehicleCount || 0,
        averageSpeed: payload.averageSpeed || 0,
        pollutionIndex: payload.pollutionIndex || 0,
        signalPhase: payload.signalPhase || 'green',
        congestionLevel: payload.congestionLevel || 'moderate'
      });

      await event.save();
      io.emit('trafficUpdate', event);
    } catch (err) {
      console.error('Failed handling MQTT message', err);
    }
  });

  client.on('error', (err) => {
    console.error('MQTT client error:', err);
  });

  return client;
}

module.exports = startMqttBridge;
