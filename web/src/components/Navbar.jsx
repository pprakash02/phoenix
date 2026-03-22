import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-left">
          <Link to="/" className="navbar-brand">
            <span className="brand-icon">🔥</span>
            <span className="brand-text">PHOENIX</span>
          </Link>
          <div className="navbar-links">
            <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
              Setup
            </Link>
            <Link to="/progress" className={`nav-link ${isActive('/progress') ? 'active' : ''}`}>
              Pipeline
            </Link>
            <Link to="/results" className={`nav-link ${isActive('/results') ? 'active' : ''}`}>
              Results
            </Link>
          </div>
        </div>
        <div className="navbar-right">
          <div className="nav-status-dot" title="Server Status"></div>
          <button className="nav-deploy-btn">Deploy</button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
