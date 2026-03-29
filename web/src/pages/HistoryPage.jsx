import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getHistory } from '../services/api';
import './HistoryPage.css';

function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    try {
      setLoading(true);
      const data = await getHistory();
      setHistory(data.history || []);
    } catch (err) {
      setError(err.message || 'Failed to load history');
    } finally {
      setLoading(false);
    }
  }

  function getStatusLabel(status) {
    const map = {
      started: { text: 'In Progress', cls: 'amber' },
      running: { text: 'In Progress', cls: 'amber' },
      completed: { text: 'Completed', cls: 'green' },
      approved: { text: 'Completed', cls: 'green' },
      error: { text: 'Failed', cls: 'red' },
    };
    return map[status] || { text: status || 'Unknown', cls: 'gray' };
  }

  function formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  function extractRepoName(url) {
    if (!url) return 'Unknown';
    const match = url.match(/github\.com\/([^/]+\/[^/]+)/);
    return match ? match[1] : url;
  }

  const filteredHistory = history
    .filter(h => filter === 'all' || h.status === filter)
    .filter(h => {
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      return (
        (h.repo_url || '').toLowerCase().includes(q) ||
        (h.session_id || '').toLowerCase().includes(q) ||
        (h.llm_model || '').toLowerCase().includes(q)
      );
    });

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner large"></div>
        <p>Loading history…</p>
      </div>
    );
  }

  return (
    <div className="history-page container-wide animate-fade-in">
      <div className="history-header">
        <div>
          <h1 className="history-title">Run History</h1>
          <p className="history-subtitle">
            All your previous analysis runs and their results.
          </p>
        </div>
        <div className="history-stats">
          <div className="history-stat">
            <span className="history-stat-value">{history.length}</span>
            <span className="history-stat-label">Total Runs</span>
          </div>
          <div className="history-stat">
            <span className="history-stat-value">
              {history.filter(h => h.status === 'completed').length}
            </span>
            <span className="history-stat-label">Completed</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="history-toolbar">
        <div className="history-filters">
          {['all', 'completed', 'started', 'error'].map(f => (
            <button
              key={f}
              className={`history-filter-btn ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <input
          type="text"
          className="history-search ph-input"
          placeholder="Search by repo, session, or model…"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          id="history-search-input"
        />
      </div>

      {error && <div className="ph-error">{error}</div>}

      {filteredHistory.length === 0 ? (
        <div className="empty-state-card">
          <span className="empty-icon">📋</span>
          <h2>No runs found</h2>
          <p>
            {history.length === 0
              ? "You haven't started any analysis yet."
              : 'No runs match your current filter.'}
          </p>
          {history.length === 0 && (
            <Link to="/" className="ph-btn-primary" id="history-start-btn">
              Start Your First Analysis
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 8h10M9 4l4 4-4 4"/>
              </svg>
            </Link>
          )}
        </div>
      ) : (
        <div className="history-list">
          {filteredHistory.map((entry, i) => {
            const status = getStatusLabel(entry.status);
            const isExpanded = expandedId === entry.id;

            return (
              <div
                key={entry.id || i}
                className={`history-card ${isExpanded ? 'expanded' : ''}`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div
                  className="history-card-main"
                  onClick={() => setExpandedId(isExpanded ? null : entry.id)}
                  id={`history-entry-${entry.id}`}
                >
                  <div className="history-card-left">
                    <div className="history-repo-name">
                      {extractRepoName(entry.repo_url)}
                    </div>
                    <div className="history-meta">
                      <span className="history-session-id">{entry.session_id}</span>
                      <span className="history-date">{formatDate(entry.created_at)}</span>
                    </div>
                  </div>
                  <div className="history-card-right">
                    <span className={`ph-chip ${status.cls}`}>{status.text}</span>
                    <span className="history-model">{entry.llm_model || '—'}</span>
                    <svg
                      className={`history-chevron ${isExpanded ? 'open' : ''}`}
                      width="16" height="16" viewBox="0 0 16 16"
                      fill="none" stroke="currentColor" strokeWidth="2"
                    >
                      <path d="M4 6l4 4 4-4"/>
                    </svg>
                  </div>
                </div>

                {isExpanded && (
                  <div className="history-card-details animate-fade-in">
                    <div className="history-detail-grid">
                      <div className="history-detail-item">
                        <span className="history-detail-label">Repository</span>
                        <span className="history-detail-value">
                          <a href={entry.repo_url} target="_blank" rel="noopener noreferrer">
                            {entry.repo_url}
                          </a>
                        </span>
                      </div>
                      <div className="history-detail-item">
                        <span className="history-detail-label">Files Analyzed</span>
                        <span className="history-detail-value">{entry.total_files || '—'}</span>
                      </div>
                      <div className="history-detail-item">
                        <span className="history-detail-label">Functions</span>
                        <span className="history-detail-value">{entry.total_functions || '—'}</span>
                      </div>
                      <div className="history-detail-item">
                        <span className="history-detail-label">Completed</span>
                        <span className="history-detail-value">{formatDate(entry.completed_at)}</span>
                      </div>
                      {entry.results_summary && (
                        <>
                          <div className="history-detail-item">
                            <span className="history-detail-label">Test Files</span>
                            <span className="history-detail-value">{entry.results_summary.test_files || 0}</span>
                          </div>
                          <div className="history-detail-item">
                            <span className="history-detail-label">Doc Files</span>
                            <span className="history-detail-value">{entry.results_summary.doc_files || 0}</span>
                          </div>
                        </>
                      )}
                      {entry.error && (
                        <div className="history-detail-item full-width">
                          <span className="history-detail-label">Error</span>
                          <span className="history-detail-value error-text">{entry.error}</span>
                        </div>
                      )}
                    </div>
                    {entry.session_id && (entry.status === 'completed' || entry.status === 'approved') && (
                      <div className="history-detail-actions">
                        <Link
                          to={`/results?session=${entry.session_id}`}
                          className="ph-btn-primary"
                          id={`view-results-${entry.id}`}
                        >
                          View Results
                          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 8h10M9 4l4 4-4 4"/>
                          </svg>
                        </Link>
                      </div>
                    )}
                    {entry.session_id && (entry.status === 'started' || entry.status === 'running') && (
                      <div className="history-detail-actions">
                        <Link
                          to="/progress"
                          className="ph-btn-primary history-progress-btn"
                          id={`view-progress-${entry.id}`}
                        >
                          <span className="progress-pulse-dot" />
                          View Progress
                          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 8h10M9 4l4 4-4 4"/>
                          </svg>
                        </Link>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default HistoryPage;
