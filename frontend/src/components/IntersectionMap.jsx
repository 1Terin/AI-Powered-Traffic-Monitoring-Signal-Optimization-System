const INTERSECTIONS = ['A1', 'B2', 'C3', 'D4'];
const PHASE_COLORS = {
  green: '#27ae60',
  yellow: '#f2c94c',
  red: '#eb5757'
};

export default function IntersectionMap({ signals, latestByIntersection }) {
  return (
    <div className="intersection-map">
      <h3>Intersection map</h3>
      <div className="map-grid">
        {INTERSECTIONS.map((id) => {
          const signal = signals[id];
          const latest = latestByIntersection[id];
          const phase = signal?.phase || latest?.signalPhase || 'green';
          const vehicles = latest?.vehicleCount ?? 0;
          return (
            <div key={id} className="map-node" style={{ borderColor: PHASE_COLORS[phase] || '#64748b' }}>
              <strong>{id}</strong>
              <span className="phase-badge" style={{ background: PHASE_COLORS[phase] }}>{phase}</span>
              <small>{vehicles} vehicles</small>
            </div>
          );
        })}
      </div>
    </div>
  );
}
