import TrafficDashboard from './components/TrafficDashboard';

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>AI Traffic Monitoring Dashboard</h1>
          <p>Real-time intersection flow, speed, and pollution metrics.</p>
        </div>
      </header>
      <main>
        <TrafficDashboard />
      </main>
    </div>
  );
}
