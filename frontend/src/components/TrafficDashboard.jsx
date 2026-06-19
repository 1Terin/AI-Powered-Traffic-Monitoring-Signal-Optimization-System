import { useEffect, useMemo, useState } from 'react';
import { io } from 'socket.io-client';
import TrafficCharts from './TrafficCharts';
import CameraDetectionsPanel from './CameraDetectionsPanel';
import IntersectionMap from './IntersectionMap';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000';

function formatNumber(value) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
}

function formatSensorType(value) {
  if (!value) return 'unknown';
  return value.replace(/_/g, ' ');
}

export default function TrafficDashboard() {
  const [summary, setSummary] = useState({ averageSpeed: 0, averagePollution: 0, totalVehicles: 0 });
  const [latestEvent, setLatestEvent] = useState({
    intersection: '-',
    signalPhase: '-',
    congestionLevel: '-',
    sensorType: '-'
  });
  const [history, setHistory] = useState([]);
  const [detections, setDetections] = useState([]);
  const [signals, setSignals] = useState({});
  const [forecast, setForecast] = useState(null);
  const [status, setStatus] = useState('Connecting to live feed...');

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [summaryRes, detectionsRes, signalsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/traffic/summary`),
          fetch(`${API_BASE_URL}/api/detections`),
          fetch(`${API_BASE_URL}/api/signals`)
        ]);
        setSummary(await summaryRes.json());
        setDetections(await detectionsRes.json());
        setSignals(await signalsRes.json());
      } catch (error) {
        console.error(error);
      }
    }

    loadInitialData();

    const socket = io(API_BASE_URL, {
      transports: ['websocket']
    });

    socket.on('connect', () => setStatus('Live data connected'));
    socket.on('disconnect', () => setStatus('Disconnected from live feed'));
    socket.on('signalUpdate', (update) => {
      setSignals((current) => ({
        ...current,
        [update.intersection]: {
          phase: update.phase,
          duration: update.duration
        }
      }));
    });
    socket.on('cameraDetection', (detection) => {
      setDetections((current) => [detection, ...current].slice(0, 20));
    });
    socket.on('trafficUpdate', (event) => {
      setHistory((current) => {
        const next = [...current, event].slice(-20);

        setLatestEvent({
          intersection: event.intersection,
          signalPhase: event.signalPhase,
          congestionLevel: event.congestionLevel,
          sensorType: event.sensorType || 'aggregated'
        });

        setSummary((previous) => ({
          averageSpeed: (previous.averageSpeed + event.averageSpeed) / 2,
          averagePollution: (previous.averagePollution + event.pollutionIndex) / 2,
          totalVehicles: previous.totalVehicles + event.vehicleCount
        }));

        (async () => {
          try {
            const seqLen = 12;
            const recent = next.slice(-seqLen).map((i) => i.vehicleCount ?? 0);
            if (recent.length < seqLen) return;
            const resp = await fetch(`${API_BASE_URL}/api/predict`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ window: recent })
            });
            const json = await resp.json();
            if (json && typeof json.prediction !== 'undefined') setForecast(json.prediction);
          } catch (err) {
            // ignore forecast errors silently
          }
        })();

        return next;
      });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const chartData = useMemo(() => {
    return {
      labels: history.map((item) => new Date(item.timestamp).toLocaleTimeString()),
      vehicleCounts: history.map((item) => item.vehicleCount),
      speeds: history.map((item) => item.averageSpeed),
      pollution: history.map((item) => item.pollutionIndex)
    };
  }, [history]);

  const latestByIntersection = useMemo(() => {
    const map = {};
    history.forEach((event) => {
      map[event.intersection] = event;
    });
    return map;
  }, [history]);

  return (
    <section className="dashboard-card">
      <div className="dashboard-header">
        <div>
          <h2>Live traffic insights</h2>
          <p>{status}</p>
        </div>
        <div className="summary-grid">
          <div className="summary-card">
            <span className="summary-label">Vehicles / min</span>
            <strong>{formatNumber(summary.totalVehicles)}</strong>
          </div>
          <div className="summary-card">
            <span className="summary-label">Avg speed (km/h)</span>
            <strong>{formatNumber(summary.averageSpeed)}</strong>
          </div>
          <div className="summary-card">
            <span className="summary-label">Air quality index</span>
            <strong>{formatNumber(summary.averagePollution)}</strong>
          </div>
        </div>
      </div>
      <div className="details-grid">
        <div className="summary-card">
          <span className="summary-label">Intersection</span>
          <strong>{latestEvent.intersection}</strong>
        </div>
        <div className="summary-card">
          <span className="summary-label">Signal phase</span>
          <strong>{latestEvent.signalPhase}</strong>
        </div>
        <div className="summary-card">
          <span className="summary-label">Congestion</span>
          <strong>{latestEvent.congestionLevel}</strong>
        </div>
        <div className="summary-card">
          <span className="summary-label">Sensor source</span>
          <strong>{formatSensorType(latestEvent.sensorType)}</strong>
        </div>
        <div className="summary-card">
          <span className="summary-label">LSTM forecast</span>
          <strong>{forecast !== null ? formatNumber(forecast) : 'loading...'}</strong>
        </div>
      </div>
      <div className="panels-grid">
        <IntersectionMap signals={signals} latestByIntersection={latestByIntersection} />
        <CameraDetectionsPanel detections={detections} />
      </div>
      <TrafficCharts data={chartData} />
    </section>
  );
}
