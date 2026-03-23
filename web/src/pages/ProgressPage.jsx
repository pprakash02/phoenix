import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from '../hooks/useSocket';
import SetupProgress from '../components/SetupProgress';
import './ProgressPage.css';

const STAGE_ORDER = ['preparing', 'analyzing', 'running', 'observing', 'generating', 'validating', 'fixing', 'documenting', 'complete'];
const STAGE_LABELS = {
  preparing: 'Preparing Workspace',
  analyzing: 'Analyzing Code',
  running: 'Starting Pipeline',
  observing: 'Observer Agent',
  generating: 'QA Engineer Agent',
  validating: 'Critic Agent',
  fixing: 'Fix Iteration',
  documenting: 'Documentation Writer',
  complete: 'Complete',
};

function ProgressPage({ sessionData }) {
  const navigate = useNavigate();
  const sessionId = sessionData?.session_id;
  const { isConnected, progress, pipelineResult, error } = useSocket(sessionId);
  const [stages, setStages] = useState([]);
  const [contextInput, setContextInput] = useState('');
  const maxProgressRef = useRef(0);

  useEffect(() => {
    if (progress) {
      setStages((prev) => {
        const exists = prev.find((s) => s.stage === progress.stage);
        if (exists) {
          return prev.map((s) => s.stage === progress.stage ? { ...s, ...progress } : s);
        }
        return [...prev, progress];
      });
    }
  }, [progress]);

  useEffect(() => {
    if (pipelineResult) {
      navigate('/review');
    }
  }, [pipelineResult, navigate]);

  if (!sessionId) {
    return (
      <div className="progress-page animate-fade-in">
        <div className="page-two-col">
          <div className="page-left">
            <SetupProgress currentStep={2} />
          </div>
          <div className="page-right">
            <div className="empty-state-card">
              <span className="empty-icon">🚀</span>
              <h2>No Active Pipeline</h2>
              <p>Start a project from the Setup page to begin.</p>
              <button className="ph-btn-primary" onClick={() => navigate('/')}>Go to Setup</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentStage = progress?.stage || 'preparing';
  // Unidirectional: only allow increases, cap at 100%
  const rawProgress = Math.min(progress?.progress || 0, 100);
  if (rawProgress > maxProgressRef.current) {
    maxProgressRef.current = rawProgress;
  }
  const progressPercent = maxProgressRef.current;

  return (
    <div className="progress-page animate-fade-in">
      <div className="page-two-col">
        {/* ─── Left Sidebar ─── */}
        <div className="page-left">
          <div className="sidebar-badge">
            <span className="badge-dot pulse" />
            Pipeline Running
          </div>
          <h1 className="sidebar-title">Agent<br /><span>Pipeline</span></h1>
          <p className="sidebar-description">
            Phoenix agents are analyzing your codebase, generating tests,
            and writing documentation.
          </p>

          <div className="connection-badge">
            <span className={`conn-dot ${isConnected ? 'connected' : 'disconnected'}`} />
            <span>{isConnected ? 'Connected' : 'Reconnecting...'}</span>
            <span className="session-id">{sessionId}</span>
          </div>

          <SetupProgress currentStep={2} />
        </div>

        {/* ─── Right Panel ─── */}
        <div className="page-right">
          <div className="panel-card">
            {error && (
              <div className="pipeline-error">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="currentColor">
                  <path d="M9 1a8 8 0 1 0 0 16A8 8 0 0 0 9 1zm-.85 4.5a.85.85 0 0 1 1.7 0v3.4a.85.85 0 0 1-1.7 0V5.5zM9 13a.85.85 0 1 1 0-1.7.85.85 0 0 1 0 1.7z"/>
                </svg>
                <div>
                  <strong>Pipeline Error</strong>
                  <p>{error}</p>
                </div>
              </div>
            )}

            {/* Progress Bar */}
            <div className="progress-bar-section">
              <div className="progress-bar-header">
                <span className="progress-bar-title">Overall Progress</span>
                <span className="progress-pct">{progressPercent}%</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
              </div>
            </div>

            {/* Stage Timeline */}
            <div className="stage-timeline">
              {STAGE_ORDER.map((stageKey, idx) => {
                const stageData = stages.find((s) => s.stage === stageKey);
                const isActive = currentStage === stageKey;
                const isPast = STAGE_ORDER.indexOf(currentStage) > STAGE_ORDER.indexOf(stageKey);
                const isFuture = !isActive && !isPast;
                const isLast = idx === STAGE_ORDER.length - 1;

                return (
                  <div
                    key={stageKey}
                    className={`tl-item ${isActive ? 'active' : ''} ${isPast ? 'completed' : ''} ${isFuture ? 'future' : ''}`}
                  >
                    <div className="tl-track">
                      <div className="tl-marker">
                        {isPast ? (
                          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M3 7l3 3 5-5" />
                          </svg>
                        ) : (
                          <span className="tl-num">{idx + 1}</span>
                        )}
                      </div>
                      {!isLast && <div className="tl-line" />}
                    </div>
                    <div className="tl-content">
                      <span className="tl-label">{STAGE_LABELS[stageKey]}</span>
                      {stageData && (
                        <span className="tl-message">{stageData.message}</span>
                      )}
                      {isActive && !error && stageKey !== 'complete' && (
                        <div className="tl-pulse">
                          <span className="tl-pulse-dot" />
                          Processing...
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Context Input */}
            <div className="waiting-context">
              <h3>💡 Add Additional Context While Waiting</h3>
              <p>You can provide additional context that will be passed to the agents in the next iteration.</p>
              <textarea
                className="ph-textarea"
                placeholder="e.g., Focus on error handling paths, test database connection failures..."
                value={contextInput}
                onChange={(e) => setContextInput(e.target.value)}
                rows={3}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProgressPage;
