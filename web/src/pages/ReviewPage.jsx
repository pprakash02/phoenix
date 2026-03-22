import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getResults, approveTests, rejectTests } from '../services/api';
import { useSocket } from '../hooks/useSocket';
import './ReviewPage.css';

function ReviewPage({ sessionData }) {
  const navigate = useNavigate();
  const sessionId = sessionData?.session_id;
  const { pipelineResult } = useSocket(sessionId);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(null);
  const [showReject, setShowReject] = useState(false);
  const [rejectComments, setRejectComments] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (pipelineResult) {
      setResults(pipelineResult);
      setLoading(false);
      const firstFile = Object.keys(pipelineResult.test_files || {})[0];
      if (firstFile) setActiveTab(firstFile);
    } else if (sessionId) {
      getResults(sessionId)
        .then((data) => {
          setResults(data);
          const firstFile = Object.keys(data.test_files || {})[0];
          if (firstFile) setActiveTab(firstFile);
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
        <div className="container">
          <div className="empty-state">
            <span className="empty-icon">📋</span>
            <h2>No Results to Review</h2>
            <p>Run a pipeline first to generate test suites.</p>
            <button className="btn-primary" onClick={() => navigate('/')}>Go to Setup</button>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="review-page animate-fade-in">
        <div className="container">
          <div className="loading-state">
            <span className="spinner large" />
            <p>Loading results...</p>
          </div>
        </div>
      </div>
    );
  }

  const testFiles = results?.test_files || {};
  const docFiles = results?.doc_files || {};
  const conversationLog = results?.conversation_log || [];

  return (
    <div className="review-page animate-fade-in">
      <div className="container-wide">
        <div className="page-header">
          <span className="page-subtitle">QUALITY REVIEW</span>
          <h1 className="page-title">Review Generated Tests</h1>
          <p className="page-desc">
            Review the auto-generated test suites and documentation before approval.
          </p>
        </div>

        <div className="review-stats">
          <div className="stat-card">
            <span className="stat-value">{Object.keys(testFiles).length}</span>
            <span className="stat-label">Test Files</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{Object.keys(docFiles).length}</span>
            <span className="stat-label">Doc Files</span>
          </div>
          <div className="stat-card accent">
            <span className="stat-value">{conversationLog.length}</span>
            <span className="stat-label">Agent Messages</span>
          </div>
        </div>

        {/* Test File Tabs */}
        <div className="code-viewer">
          <div className="code-tabs">
            {Object.keys(testFiles).map((fname) => (
              <button
                key={fname}
                className={`code-tab ${activeTab === fname ? 'active' : ''}`}
                onClick={() => setActiveTab(fname)}
              >
                🧪 {fname}
              </button>
            ))}
            {Object.keys(docFiles).map((fname) => (
              <button
                key={fname}
                className={`code-tab ${activeTab === fname ? 'active' : ''}`}
                onClick={() => setActiveTab(fname)}
              >
                📄 {fname}
              </button>
            ))}
          </div>

          <div className="code-content">
            <pre><code>{testFiles[activeTab] || docFiles[activeTab] || 'Select a file to view'}</code></pre>
          </div>
        </div>

        {/* Agent Conversation Log */}
        {conversationLog.length > 0 && (
          <div className="conversation-section">
            <h3>🤖 Agent Conversation</h3>
            <div className="conversation-log">
              {conversationLog.map((msg, idx) => (
                <div key={idx} className={`conversation-msg ${msg.author.toLowerCase()}`}>
                  <div className="msg-header">
                    <span className="msg-author">{msg.author}</span>
                  </div>
                  <div className="msg-content">
                    <pre>{msg.content.slice(0, 500)}{msg.content.length > 500 ? '...' : ''}</pre>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Reject Modal */}
        {showReject && (
          <div className="reject-modal-overlay" onClick={() => setShowReject(false)}>
            <div className="reject-modal" onClick={(e) => e.stopPropagation()}>
              <h3>📝 Rejection Comments</h3>
              <p>Describe what needs improvement. The pipeline will re-run with your feedback.</p>
              <textarea
                className="form-textarea"
                placeholder="e.g., Missing edge cases for empty lists, need boundary tests for negative inputs..."
                value={rejectComments}
                onChange={(e) => setRejectComments(e.target.value)}
                rows={4}
              />
              <div className="modal-actions">
                <button className="btn-secondary" onClick={() => setShowReject(false)}>Cancel</button>
                <button className="btn-danger" onClick={handleReject} disabled={actionLoading}>
                  {actionLoading ? <span className="spinner" /> : 'Submit & Re-run'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Approval Actions */}
        <div className="review-actions">
          <button
            className="btn-reject"
            onClick={() => setShowReject(true)}
            disabled={actionLoading}
          >
            ✗ Reject with Comments
          </button>
          <button
            className="btn-approve"
            onClick={handleApprove}
            disabled={actionLoading}
          >
            {actionLoading ? <span className="spinner" /> : '✓ Approve & Continue'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ReviewPage;
