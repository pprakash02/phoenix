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
            <span className="brand-logo">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <rect width="28" height="28" rx="8" fill="#6C5CE7"/>
                <path d="M8 14L12 8L16 14L20 8" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M8 20L12 14L16 20L20 14" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.6"/>
              </svg>
            </span>
            <span className="brand-text">Phoenix</span>
          </Link>
        </div>

        <div className="navbar-center">
          <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
            Dashboard
          </Link>
          <Link to="/results" className={`nav-link ${isActive('/results') ? 'active' : ''}`}>
            Projects
          </Link>
        </div>

        <div className="navbar-right">
          <button className="nav-icon-btn" title="Notifications">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M15 7.5a5 5 0 0 0-10 0c0 5.833-2.5 7.5-2.5 7.5h15S15 13.333 15 7.5"/>
              <path d="M11.45 17.5a1.667 1.667 0 0 1-2.9 0"/>
            </svg>
          </button>
          <div className="nav-avatar">
            <img
              src="https://api.dicebear.com/7.x/avataaars/svg?seed=phoenix"
              alt="User"
              width="32"
              height="32"
            />
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
