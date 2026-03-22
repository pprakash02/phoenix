import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from '../hooks/useSocket';
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
const STAGE_ICONS = {
  preparing: '⚙️',
  analyzing: '🔍',
  running: '🚀',
  observing: '👁️',
  generating: '🧪',
  validating: '✅',
  fixing: '🔧',
  documenting: '📝',
  complete: '🎉',
};

function ProgressPage({ sessionData }) {
  const navigate = useNavigate();
  const sessionId = sessionData?.session_id;
  const { isConnected, progress, pipelineResult, error } = useSocket(sessionId);
  const [stages, setStages] = useState([]);
  const [contextInput, setContextInput] = useState('');

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
        <div className="container">
          <div className="empty-state">
            <span className="empty-icon">🚀</span>
            <h2>No Active Pipeline</h2>
            <p>Start a project from the Setup page to begin.</p>
            <button className="btn-primary" onClick={() => navigate('/')}>Go to Setup</button>
          </div>
        </div>
      </div>
    );
  }

  const currentStage = progress?.stage || 'preparing';
  const progressPercent = progress?.progress || 0;

  return (
    <div className="progress-page animate-fade-in">
      <div className="container">
        <div className="page-header">
          <span className="page-subtitle">PIPELINE EXECUTION</span>
          <h1 className="page-title">Agent Pipeline</h1>
          <div className="connection-status">
            <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
            <span className="status-text">{isConnected ? 'Connected' : 'Reconnecting...'}</span>
            <span className="session-badge">{sessionId}</span>
          </div>
        </div>

        {error && (
          <div className="pipeline-error">
            <span className="error-icon">❌</span>
            <div>
              <strong>Pipeline Error</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        <div className="progress-bar-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
          </div>
          <span className="progress-label">{progressPercent}%</span>
        </div>

        {/* Stage Timeline */}
        <div className="stage-timeline">
          {STAGE_ORDER.map((stageKey) => {
            const stageData = stages.find((s) => s.stage === stageKey);
            const isActive = currentStage === stageKey;
            const isPast = STAGE_ORDER.indexOf(currentStage) > STAGE_ORDER.indexOf(stageKey);
            const isFuture = !isActive && !isPast;

            return (
              <div
                key={stageKey}
                className={`timeline-item ${isActive ? 'active' : ''} ${isPast ? 'completed' : ''} ${isFuture ? 'future' : ''}`}
              >
                <div className="timeline-marker">
                  {isPast ? '✓' : STAGE_ICONS[stageKey]}
                </div>
                <div className="timeline-content">
                  <span className="timeline-label">{STAGE_LABELS[stageKey]}</span>
                  {stageData && (
                    <span className="timeline-message">{stageData.message}</span>
                  )}
                  {isActive && !error && stageKey !== 'complete' && (
                    <div className="pulse-indicator">
                      <span className="pulse-dot" />
                      Processing...
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Context Input (available while waiting) */}
        <div className="waiting-context">
          <h3>💡 Add Additional Context While Waiting</h3>
          <p>You can provide additional context that will be passed to the agents in the next iteration.</p>
          <textarea
            className="form-textarea"
            placeholder="e.g., Focus on error handling paths, test database connection failures..."
            value={contextInput}
            onChange={(e) => setContextInput(e.target.value)}
            rows={3}
          />
        </div>
      </div>
    </div>
  );
}

export default ProgressPage;
