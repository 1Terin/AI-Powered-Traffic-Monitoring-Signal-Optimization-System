function formatTime(value) {
  return new Date(value).toLocaleTimeString();
}

export default function CameraDetectionsPanel({ detections }) {
  const latest = detections[0];

  return (
    <div className="camera-panel">
      <h3>PTZ camera detections (YOLO)</h3>
      {latest ? (
        <>
          <div className="camera-meta">
            <span>{latest.cameraId || 'PTZ-1'}</span>
            <span>{latest.intersection || 'A1'}</span>
            <span>{formatTime(latest.timestamp)}</span>
          </div>
          <p className="camera-count">{latest.count ?? latest.detections?.length ?? 0} vehicles detected</p>
          <ul className="detection-list">
            {(latest.detections || []).slice(0, 6).map((item, index) => (
              <li key={`${latest.frame}-${index}`}>
                <span>{item.class || 'vehicle'}</span>
                <span>{Math.round((item.confidence || item.conf || 0) * 100)}%</span>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <p className="muted">Waiting for camera detections...</p>
      )}
    </div>
  );
}
