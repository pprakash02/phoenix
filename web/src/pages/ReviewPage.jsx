import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { getResults, approveTests, rejectTests } from '../services/api';
import { useSocket, clearAllPipelineState } from '../hooks/useSocket';
import SetupProgress from '../components/SetupProgress';
import './ReviewPage.css';

function ReviewPage({ sessionData }) {
  const navigate = useNavigate();
  const sessionId = sessionData?.session_id;
  const { pipelineResult } = useSocket(sessionId);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedFile, setExpandedFile] = useState(null);
  const [showReject, setShowReject] = useState(false);
  const [rejectComments, setRejectComments] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (pipelineResult) {
      setResults(pipelineResult);
      setLoading(false);
    } else if (sessionId) {
      getResults(sessionId)
        .then((data) => {
          setResults(data);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [sessionId, pipelineResult]);

  const handleApprove = async () => {
    setActionLoading(true);
    try {
      await approveTests(sessionId);
      navigate('/results');
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    setActionLoading(true);
    try {
      await rejectTests(sessionId, rejectComments);
      setShowReject(false);
      // Clear old pipeline state so progress page starts fresh for the re-run
      clearAllPipelineState();
      navigate('/progress');
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  if (!sessionId) {
    return (
      <div className="review-page animate-fade-in">
        <div className="page-two-col">
          <div className="page-left"><SetupProgress currentStep={2} /></div>
          <div className="page-right">
            <div className="empty-state-card">
              <svg className="empty-icon-svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
                <rect x="9" y="3" width="6" height="4" rx="2" />
              </svg>
              <h2>No Results to Review</h2>
              <p>Run a pipeline first to generate test suites.</p>
              <button className="ph-btn-primary" onClick={() => navigate('/')}>Go to Setup</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="review-page animate-fade-in">
        <div className="page-two-col">
          <div className="page-left"><SetupProgress currentStep={2} /></div>
          <div className="page-right">
            <div className="empty-state-card">
              <span className="spinner large" />
              <p>Loading results...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const testFiles = results?.test_files || {};
  const docFiles = results?.doc_files || {};
  const conversationLog = results?.conversation_log || [];
  const allFiles = [
    ...Object.entries(testFiles).map(([name, content]) => ({ name, content, type: 'test' })),
    ...Object.entries(docFiles).map(([name, content]) => ({ name, content, type: 'doc' })),
  ];

  return (
    <div className="review-page animate-fade-in">
      <div className="page-two-col">
        {/* ─── Left Sidebar ─── */}
        <div className="page-left">
          <div className="sidebar-badge">
            <span className="badge-dot" />
            Quality Review
          </div>
          <h1 className="sidebar-title">Review<br /><span>Generated Tests</span></h1>
          <p className="sidebar-description">
            Review the auto-generated test suites and documentation before approval.
          </p>

          <div className="review-stats-sidebar">
            <div className="mini-stat">
              <span className="mini-stat-value">{Object.keys(testFiles).length}</span>
              <span className="mini-stat-label">Test Files</span>
            </div>
            <div className="mini-stat">
              <span className="mini-stat-value">{Object.keys(docFiles).length}</span>
              <span className="mini-stat-label">Doc Files</span>
            </div>
            <div className="mini-stat accent">
              <span className="mini-stat-value">{conversationLog.length}</span>
              <span className="mini-stat-label">Messages</span>
            </div>
          </div>

          <SetupProgress currentStep={2} />
        </div>

        {/* ─── Right Panel ─── */}
        <div className="page-right">
          <div className="panel-card">
            <h2 className="panel-section-title">Generated Files</h2>
            <p className="panel-section-desc">Click on a file to expand and review its content.</p>

            {/* Expandable File Cards */}
            <div className="review-file-list">
              {allFiles.map((file, index) => (
                <div
                  key={file.name}
                  className={`review-file-card animate-slide-up ${expandedFile === file.name ? 'expanded' : ''}`}
                  style={{ animationDelay: `${index * 40}ms` }}
                >
                  <div
                    className="review-file-header"
                    onClick={() => setExpandedFile(expandedFile === file.name ? null : file.name)}
                  >
                    <div className="review-file-info">
                      <span className="review-file-icon">
                        {file.type === 'test' ? (
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="#6C5CE7" strokeWidth="1.5">
                            <path d="M6 3l4 5-4 5" />
                            <circle cx="8" cy="8" r="7" />
                          </svg>
                        ) : (
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="#10b981" strokeWidth="1.5">
                            <path d="M3 2h7l3 3v9H3z" />
                            <path d="M5 7h6M5 10h4" />
                          </svg>
                        )}
                      </span>
                      <div>
                        <span className="review-file-name">{file.name}</span>
                        <span className="review-file-meta">
                          {file.content.split('\n').length} lines · {(file.content.length / 1024).toFixed(1)} KB
                        </span>
                      </div>
                    </div>
                    <div className="review-file-right">
                      <span className={`ph-chip ${file.type === 'test' ? 'purple' : 'green'}`}>
                        {file.type === 'test' ? 'TEST' : 'DOCS'}
                      </span>
                      <span className="expand-icon">{expandedFile === file.name ? '▲' : '▼'}</span>
                    </div>
                  </div>

                  {expandedFile === file.name && (
                    <div className="review-file-body">
                      {file.type === 'doc' ? (
                        <div className="markdown-content">
                          <ReactMarkdown>{file.content}</ReactMarkdown>
                        </div>
                      ) : (
                        <pre className="code-block"><code>{file.content}</code></pre>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Agent Conversation Log */}
            {conversationLog.length > 0 && (
              <div className="conversation-section">
                <h3>
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#6C5CE7" strokeWidth="1.5" style={{verticalAlign: 'middle', marginRight: '6px'}}>
                    <circle cx="9" cy="9" r="7" />
                    <path d="M9 6v4M6 13h6" />
                  </svg>
                  Agent Conversation
                </h3>
                <div className="conversation-log">
                  {conversationLog.slice(0, 20).map((msg, idx) => (
                    <div key={idx} className={`conversation-msg ${msg.author.toLowerCase()}`}>
                      <div className="msg-header">
                        <span className="msg-author">{msg.author}</span>
                      </div>
                      <div className="msg-content">
                        <pre>{msg.content.slice(0, 300)}{msg.content.length > 300 ? '...' : ''}</pre>
                      </div>
                    </div>
                  ))}
                  {conversationLog.length > 20 && (
                    <div className="msg-overflow">
                      + {conversationLog.length - 20} more messages
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Approval Actions */}
            <div className="panel-footer review-footer">
              <button
                className="ph-btn-outline-danger"
                onClick={() => setShowReject(true)}
                disabled={actionLoading}
              >
                ✗ Reject with Comments
              </button>
              <button
                className="ph-btn-primary"
                onClick={handleApprove}
                disabled={actionLoading}
              >
                {actionLoading ? <span className="spinner" /> : '✓ Approve & Continue'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Reject Modal */}
      {showReject && (
        <div className="modal-overlay" onClick={() => setShowReject(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" style={{verticalAlign: 'middle', marginRight: '4px'}}>
                <path d="M3 3h10v10H3z" />
                <path d="M6 6h4M6 9h2" />
              </svg>
              Rejection Comments
            </h3>
            <p>Describe what needs improvement. The pipeline will re-run with your feedback.</p>
            <textarea
              className="ph-textarea"
              placeholder="e.g., Missing edge cases for empty lists, need boundary tests for negative inputs..."
              value={rejectComments}
              onChange={(e) => setRejectComments(e.target.value)}
              rows={4}
            />
            <div className="modal-actions">
              <button className="ph-btn-ghost" onClick={() => setShowReject(false)}>Cancel</button>
              <button className="ph-btn-danger" onClick={handleReject} disabled={actionLoading}>
                {actionLoading ? <span className="spinner" /> : 'Submit & Re-run'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReviewPage;
