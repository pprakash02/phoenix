import './StatusBar.css';

function StatusBar({ sessionId }) {
  return (
    <footer className="status-bar">
      <div className="status-bar-inner">
        <div className="status-item">
          <span className="status-label">ENVIRONMENT</span>
          <span className="status-value">Production (US-EAST-1)</span>
        </div>
        <div className="status-divider" />
        <div className="status-item">
          <span className="status-label">VERSION</span>
          <span className="status-value">v2.5.0-WEB</span>
        </div>
        <div className="status-divider" />
        <div className="status-item">
          <span className="status-label">SESSION ID</span>
          <span className="status-value mono">{sessionId || '—'}</span>
        </div>
      </div>
      <div className="status-footer">
        <span className="footer-brand"> PHOENIX</span>
        <div className="footer-links">
          
          <span className="footer-status">STATUS: ONLINE</span>
        </div>
      </div>
    </footer>
  );
}

export default StatusBar;
