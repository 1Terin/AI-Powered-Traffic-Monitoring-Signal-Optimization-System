const mqtt = require('mqtt');
const CameraDetection = require('./models/CameraDetection');

const signalStates = new Map();

function normalizeTrafficPayload(payload, topic) {
  const sensorTypeFromTopic = topic.split('/')[1] || 'unknown';
  const sensorType = payload.sensorType || sensorTypeFromTopic;

  return {
    intersection: payload.intersection || 'A1',
    vehicleCount: Number(payload.vehicleCount) || 0,
    averageSpeed: Number(payload.averageSpeed) || 0,
    pollutionIndex: Number(payload.pollutionIndex) || 0,
    signalPhase: payload.signalPhase || signalStates.get(payload.intersection)?.phase || 'green',
    congestionLevel: payload.congestionLevel || 'moderate',
    sensorType:
      sensorType === 'inductive' || sensorType === 'inductive_loop' ? 'inductive_loop'
      : sensorType === 'airquality' || sensorType === 'air_quality' ? 'air_quality'
      : sensorType === 'traffic' || sensorType === 'aggregated' ? 'aggregated'
      : ['radar', 'camera'].includes(sensorType) ? sensorType
      : 'unknown',
    source: 'mqtt'
  };
}

function startMqttBridge(io, TrafficEvent) {
  const brokerUrl = process.env.MQTT_BROKER || 'mqtt://mqtt';
  const client = mqtt.connect(brokerUrl);

  client.on('connect', () => {
    console.log('Connected to MQTT broker at', brokerUrl);
    client.subscribe(['sensors/+/event', 'sensors/camera/detections', 'control/signals/commands'], (err) => {
      if (err) console.error('MQTT subscribe error', err);
    });
  });

  client.on('message', async (topic, msg) => {
    try {
      const payload = JSON.parse(msg.toString());

      if (topic === 'sensors/camera/detections') {
        const detection = new CameraDetection({
          cameraId: payload.cameraId || 'PTZ-1',
          intersection: payload.intersection || 'A1',
          frame: payload.frame || 0,
          count: payload.count ?? (payload.detections?.length || 0),
          detections: payload.detections || []
        });
        await detection.save();
        io.emit('cameraDetection', detection);

        const event = new TrafficEvent({
          intersection: detection.intersection,
          vehicleCount: detection.count,
          averageSpeed: 0,
          pollutionIndex: 0,
          signalPhase: signalStates.get(detection.intersection)?.phase || 'green',
          congestionLevel: detection.count > 20 ? 'high' : detection.count > 10 ? 'moderate' : 'low',
          sensorType: 'camera',
          source: 'yolo'
        });
        await event.save();
        io.emit('trafficUpdate', event);
        return;
      }

      if (topic.startsWith('control/signals/')) {
        const intersection = payload.intersection || 'A1';
        signalStates.set(intersection, {
          phase: payload.phase || payload.signalPhase || 'green',
          duration: payload.duration || 30,
          updatedAt: Date.now()
        });
        io.emit('signalUpdate', {
          intersection,
          phase: signalStates.get(intersection).phase,
          duration: signalStates.get(intersection).duration,
          action: payload.action || 'set_phase'
        });
        return;
      }

      const normalized = normalizeTrafficPayload(payload, topic);
      if (payload.signalPhase) {
        signalStates.set(normalized.intersection, {
          phase: normalized.signalPhase,
          duration: payload.duration || 30,
          updatedAt: Date.now()
        });
      }

      const event = new TrafficEvent(normalized);
      await event.save();
      io.emit('trafficUpdate', event);
    } catch (err) {
      console.error('Failed handling MQTT message on', topic, err.message || err);
    }
  });

  client.on('error', (err) => {
    console.error('MQTT client error:', err);
  });

  client.publishSignalCommand = (intersection, phase, duration = 30) => {
    const command = {
      intersection,
      action: 'set_phase',
      phase,
      duration
    };
    client.publish('control/signals/commands', JSON.stringify(command));
    signalStates.set(intersection, { phase, duration, updatedAt: Date.now() });
    io.emit('signalUpdate', { intersection, phase, duration, action: 'set_phase' });
  };

  client.getSignalStates = () => Object.fromEntries(signalStates);

  return client;
}

module.exports = startMqttBridge;
