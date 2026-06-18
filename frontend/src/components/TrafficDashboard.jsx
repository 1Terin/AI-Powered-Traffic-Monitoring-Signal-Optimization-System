import { useEffect, useMemo, useState } from 'react';
import { io } from 'socket.io-client';
import TrafficCharts from './TrafficCharts';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000';

function formatNumber(value) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
}

export default function TrafficDashboard() {
  const [summary, setSummary] = useState({ averageSpeed: 0, averagePollution: 0, totalVehicles: 0 });
  const [latestEvent, setLatestEvent] = useState({ intersection: '-', signalPhase: '-', congestionLevel: '-' });
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [status, setStatus] = useState('Connecting to live feed...');

  useEffect(() => {
    async function loadSummary() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/traffic/summary`);
        const data = await response.json();
        setSummary(data);
      } catch (error) {
        console.error(error);
      }
    }

    loadSummary();

    const socket = io(API_BASE_URL, {
      transports: ['websocket']
    });

    socket.on('connect', () => setStatus('Live data connected'));
    socket.on('disconnect', () => setStatus('Disconnected from live feed'));
    socket.on('trafficUpdate', (event) => {
      setHistory((current) => {
        const next = [...current, event].slice(-20);

        setLatestEvent({
          intersection: event.intersection,
          signalPhase: event.signalPhase,
          congestionLevel: event.congestionLevel
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
          <span className="summary-label">Forecast</span>
          <strong>{forecast !== null ? formatNumber(forecast) : 'loading...'}</strong>
        </div>
      </div>
      <TrafficCharts data={chartData} />
    </section>
  );
}
