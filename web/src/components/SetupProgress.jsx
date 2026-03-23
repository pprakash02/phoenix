import { Link } from 'react-router-dom';
import './SetupProgress.css';

/**
 * Shared sidebar component that shows the setup progress steps
 * across all pages. Highlights the current step.
 *
 * @param {number} currentStep - 1, 2, or 3
 */
function SetupProgress({ currentStep = 1 }) {
  const steps = [
    { num: 1, label: 'Project Details', sub: 'Source & AI Context', path: '/' },
    { num: 2, label: 'Architecture Review', sub: 'Review generated schemas', path: '/review' },
    { num: 3, label: 'Final Results', sub: 'Download and Create PR', path: '/results' },
  ];

  return (
    <div className="sp-sidebar">
      <div className="sp-progress-section">
        <h3 className="sp-heading">SETUP PROGRESS</h3>
        <div className="sp-steps">
          {steps.map((step, idx) => {
            const isActive = currentStep === step.num;
            const isCompleted = currentStep > step.num;
            const isLast = idx === steps.length - 1;

            return (
              <div key={step.num} className="sp-step-row">
                <div className="sp-track">
                  <Link
                    to={step.path}
                    className={`sp-step-number ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                  >
                    {isCompleted ? (
                      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M3 7l3 3 5-5" />
                      </svg>
                    ) : step.num}
                  </Link>
                  {!isLast && (
                    <div className={`sp-connector ${isCompleted ? 'completed' : ''}`} />
                  )}
                </div>
                <Link
                  to={step.path}
                  className={`sp-step-content ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                >
                  <div className="sp-step-label">{step.label}</div>
                  <div className="sp-step-sublabel">{step.sub}</div>
                </Link>
              </div>
            );
          })}
        </div>
      </div>

      <div className="sp-output-section">
        <h3 className="sp-output-heading">Output</h3>
        <div className="sp-output-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="8" cy="8" r="6.5"/>
            <path d="M5.5 8L7 9.5L10.5 6" />
          </svg>
          <span>Test Suite for Legacy Functions</span>
        </div>
        <div className="sp-output-item">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="8" cy="8" r="6.5"/>
            <path d="M5.5 8L7 9.5L10.5 6" />
          </svg>
          <span>Documentation for Legacy Codebase</span>
        </div>
      </div>
    </div>
  );
}

export default SetupProgress;
