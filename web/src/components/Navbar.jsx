import { Link, useLocation } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';
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
            Create
          </Link>
          <Link to="/history" className={`nav-link ${isActive('/history') ? 'active' : ''}`} id="nav-history-link">
            History
          </Link>
          <Link to="/results" className={`nav-link ${isActive('/results') ? 'active' : ''}`}>
            Results
          </Link>
        </div>

        <div className="navbar-right" />

      </div>
    </nav>
  );
}

export default Navbar;
