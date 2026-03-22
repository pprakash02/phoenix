import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { getResults, getDownloadUrl, createPR } from '../services/api';
import './ResultsPage.css';

function ResultsPage({ sessionData }) {
  const navigate = useNavigate();
  const sessionId = sessionData?.session_id;
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(null);
  const [showPR, setShowPR] = useState(false);
  const [githubToken, setGithubToken] = useState('');
  const [branchName, setBranchName] = useState('');
  const [prLoading, setPrLoading] = useState(false);
  const [prResult, setPrResult] = useState(null);
  const [prError, setPrError] = useState('');

  useEffect(() => {
    if (sessionId) {
      getResults(sessionId)
        .then((data) => {
          setResults(data);
          const firstDoc = Object.keys(data.doc_files || {})[0];
          const firstTest = Object.keys(data.test_files || {})[0];
          setActiveTab(firstDoc || firstTest || null);
          setBranchName(`phoenix/test-suite-${sessionId}`);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [sessionId]);

  const handleCreatePR = async () => {
    if (!githubToken.trim()) {
      setPrError('GitHub token is required');
      return;
    }
    setPrLoading(true);
    setPrError('');
    try {
      const result = await createPR(sessionId, githubToken, branchName);
      setPrResult(result);
    } catch (err) {
      setPrError(err.message);
    } finally {
      setPrLoading(false);
    }
  };

  if (!sessionId) {
    return (
      <div className="results-page animate-fade-in">
        <div className="container">
          <div className="empty-state">
            <span className="empty-icon">📊</span>
            <h2>No Results Available</h2>
            <p>Complete a pipeline run to see results here.</p>
            <button className="btn-primary" onClick={() => navigate('/')}>Go to Setup</button>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="results-page animate-fade-in">
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

  return (
    <div className="results-page animate-fade-in">
      <div className="container-wide">
        <div className="page-header">
          <span className="page-subtitle">PIPELINE RESULTS</span>
          <h1 className="page-title">Generated Artifacts</h1>
          <p className="page-desc">
            Test suites and documentation ready for deployment.
          </p>
        </div>

        {/* Summary Cards */}
        <div className="results-summary">
          <div className="summary-card success">
            <div className="summary-icon">✅</div>
            <div className="summary-content">
              <span className="summary-title">Tests Generated</span>
              <span className="summary-value">{Object.keys(testFiles).length} test files</span>
            </div>
          </div>
          <div className="summary-card info">
            <div className="summary-icon">📄</div>
            <div className="summary-content">
              <span className="summary-title">Documentation</span>
              <span className="summary-value">{Object.keys(docFiles).length} doc files</span>
            </div>
          </div>
          <div className="summary-card neutral">
            <div className="summary-icon">🔥</div>
            <div className="summary-content">
              <span className="summary-title">Status</span>
              <span className="summary-value chip chip-green">PHOENIX APPROVED</span>
            </div>
          </div>
        </div>

        {/* File Viewer */}
        <div className="code-viewer">
          <div className="code-tabs">
            {Object.keys(docFiles).map((fname) => (
              <button
                key={fname}
                className={`code-tab ${activeTab === fname ? 'active' : ''}`}
                onClick={() => setActiveTab(fname)}
              >
                📄 {fname}
              </button>
            ))}
            {Object.keys(testFiles).map((fname) => (
              <button
                key={fname}
                className={`code-tab ${activeTab === fname ? 'active' : ''}`}
                onClick={() => setActiveTab(fname)}
              >
                🧪 {fname}
              </button>
            ))}
          </div>
          <div className="code-content">
            {activeTab && docFiles[activeTab] ? (
              <div className="markdown-content">
                <ReactMarkdown>{docFiles[activeTab]}</ReactMarkdown>
              </div>
            ) : (
              <pre><code>{testFiles[activeTab] || 'Select a file to view'}</code></pre>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="results-actions">
          <a
            href={getDownloadUrl(sessionId)}
            className="btn-primary download-btn"
            download
          >
            ⬇ Download All Artifacts
          </a>
          <button className="btn-primary pr-btn" onClick={() => setShowPR(true)}>
            🔀 Create Pull Request
          </button>
        </div>

        {/* PR Creation Modal */}
        {showPR && (
          <div className="reject-modal-overlay" onClick={() => setShowPR(false)}>
            <div className="reject-modal pr-modal" onClick={(e) => e.stopPropagation()}>
              <h3>🔀 Create Pull Request</h3>
              <p>Push the generated test suite and documentation to a new branch on your repository.</p>

              {prResult ? (
                <div className="pr-success">
                  <span className="pr-success-icon">🎉</span>
                  <p>Pull Request created successfully!</p>
                  <a href={prResult.url} target="_blank" rel="noopener noreferrer" className="pr-link">
                    View PR #{prResult.number} →
                  </a>
                </div>
              ) : (
                <>
                  {prError && (
                    <div className="form-error">{prError}</div>
                  )}

                  <div className="form-section">
                    <label className="form-label">GitHub Personal Access Token</label>
                    <input
                      type="password"
                      className="form-input"
                      placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                      value={githubToken}
                      onChange={(e) => setGithubToken(e.target.value)}
                    />
                    <p className="form-help">Needs 'repo' scope. Token is not stored.</p>
                  </div>

                  <div className="form-section">
                    <label className="form-label">Branch Name</label>
                    <input
                      type="text"
                      className="form-input"
                      value={branchName}
                      onChange={(e) => setBranchName(e.target.value)}
                    />
                  </div>

                  <div className="modal-actions">
                    <button className="btn-secondary" onClick={() => setShowPR(false)}>Cancel</button>
                    <button className="btn-primary" onClick={handleCreatePR} disabled={prLoading}>
                      {prLoading ? <span className="spinner" /> : 'Create PR'}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* New Project */}
        <div className="new-project-section">
          <button className="btn-secondary" onClick={() => navigate('/')}>
            ← Start New Project
          </button>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
