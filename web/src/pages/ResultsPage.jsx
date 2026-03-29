import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { getResults, getDownloadUrl } from '../services/api';
import SetupProgress from '../components/SetupProgress';
import './ResultsPage.css';

function ResultsPage({ sessionData }) {
  const navigate = useNavigate();
  const searchParams = new URLSearchParams(window.location.search);
  const urlSessionId = searchParams.get('session');
  const sessionId = sessionData?.session_id || urlSessionId;
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [expandedFile, setExpandedFile] = useState(null);

  const fetchResults = useCallback(() => {
    if (!sessionId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setFetchError(null);
    getResults(sessionId)
      .then((data) => {
        setResults(data);
        setFetchError(null);
      })
      .catch((err) => {
        setFetchError(err.message || 'Results not available yet');
      })
      .finally(() => setLoading(false));
  }, [sessionId]);

  useEffect(() => {
    fetchResults();
  }, [fetchResults]);

  // Auto-retry if results aren't ready yet (poll up to 5 times)
  const retryCountRef = {current: 0};
  useEffect(() => {
    if (fetchError && retryCountRef.current < 5) {
      const timer = setTimeout(() => {
        retryCountRef.current += 1;
        fetchResults();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [fetchError, fetchResults]);


  if (!sessionId) {
    return (
      <div className="results-page animate-fade-in">
        <div className="page-two-col">
          <div className="page-left"><SetupProgress currentStep={3} /></div>
          <div className="page-right">
            <div className="empty-state-card">
              <svg className="empty-icon-svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z" />
              </svg>
              <h2>No Results Available</h2>
              <p>Complete a pipeline run to see results here.</p>
              <button className="ph-btn-primary" onClick={() => navigate('/')}>Go to Setup</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="results-page animate-fade-in">
        <div className="page-two-col">
          <div className="page-left"><SetupProgress currentStep={3} /></div>
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

  // Error state with retry button
  if (fetchError && !results) {
    return (
      <div className="results-page animate-fade-in">
        <div className="page-two-col">
          <div className="page-left"><SetupProgress currentStep={3} /></div>
          <div className="page-right">
            <div className="empty-state-card">
              <svg className="empty-icon-svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              <h2>Results Loading</h2>
              <p>{fetchError}</p>
              <button className="ph-btn-primary" onClick={fetchResults} style={{ marginTop: '1rem' }}>
                ↻ Retry
              </button>
              <button className="ph-btn-ghost" onClick={() => navigate('/')} style={{ marginTop: '0.5rem' }}>
                ← Back to Setup
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const testFiles = results?.test_files || {};
  const docFiles = results?.doc_files || {};
  const allFiles = [
    ...Object.entries(docFiles).map(([name, content]) => ({ name, content, type: 'doc' })),
    ...Object.entries(testFiles).map(([name, content]) => ({ name, content, type: 'test' })),
  ];

  return (
    <div className="results-page animate-fade-in">
      <div className="page-two-col">
        {/* ─── Left Sidebar ─── */}
        <div className="page-left">
          <div className="sidebar-badge">
            <span className="badge-dot success" />
            Complete
          </div>
          <h1 className="sidebar-title">Generated<br /><span>Artifacts</span></h1>
          <p className="sidebar-description">
            Test suites and documentation ready for deployment.
          </p>

          <div className="results-stats-sidebar">
            <div className="result-stat-card success">
              <div className="result-stat-icon">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M6 10l3 3 5-6" />
                  <circle cx="10" cy="10" r="8" />
                </svg>
              </div>
              <div>
                <span className="result-stat-title">Tests Generated</span>
                <span className="result-stat-value">{Object.keys(testFiles).length} test files</span>
              </div>
            </div>
            <div className="result-stat-card info">
              <div className="result-stat-icon">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#6C5CE7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4 4h12v14H4z" />
                  <path d="M7 8h6M7 11h4" />
                </svg>
              </div>
              <div>
                <span className="result-stat-title">Documentation</span>
                <span className="result-stat-value">{Object.keys(docFiles).length} doc files</span>
              </div>
            </div>
            <div className="result-stat-card accent">
              <div className="result-stat-icon">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#f59e0b" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10 2l2.4 4.8L18 7.6l-4 3.9.9 5.5L10 14.4l-4.9 2.6.9-5.5-4-3.9 5.6-.8z" />
                </svg>
              </div>
              <div>
                <span className="result-stat-title">Status</span>
                <span className="ph-chip green">PHOENIX APPROVED</span>
              </div>
            </div>
          </div>

          <SetupProgress currentStep={3} />
        </div>

        {/* ─── Right Panel ─── */}
        <div className="page-right">
          <div className="panel-card">
            <h2 className="panel-section-title">All Artifacts</h2>
            <p className="panel-section-desc">
              {allFiles.length} files generated. Click to expand and review.
            </p>

            {/* Expandable File Cards */}
            <div className="results-file-list">
              {allFiles.map((file, index) => (
                <div
                  key={file.name}
                  className={`results-file-card animate-slide-up ${expandedFile === file.name ? 'expanded' : ''}`}
                  style={{ animationDelay: `${index * 40}ms` }}
                >
                  <div
                    className="results-file-header"
                    onClick={() => setExpandedFile(expandedFile === file.name ? null : file.name)}
                  >
                    <div className="results-file-info">
                      <span className="results-file-icon">
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
                        <span className="results-file-name">{file.name}</span>
                        <span className="results-file-meta">
                          {file.content.split('\n').length} lines · {(file.content.length / 1024).toFixed(1)} KB
                        </span>
                      </div>
                    </div>
                    <div className="results-file-right">
                      <span className={`ph-chip ${file.type === 'test' ? 'purple' : 'green'}`}>
                        {file.type === 'test' ? 'TEST' : 'DOCS'}
                      </span>
                      <span className="expand-icon">{expandedFile === file.name ? '▲' : '▼'}</span>
                    </div>
                  </div>

                  {expandedFile === file.name && (
                    <div className="results-file-body">
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

            {/* Actions */}
            <div className="panel-footer">
              <button className="ph-btn-ghost" onClick={() => navigate('/')}>
                ← Start New Project
              </button>
              <div className="footer-actions-right">
                <a
                  href={getDownloadUrl(sessionId)}
                  className="ph-btn-primary download-link"
                  download
                >
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M8 2v9M4 8l4 4 4-4M2 14h12" />
                  </svg>
                  Download All
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
