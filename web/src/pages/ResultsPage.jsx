import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { getResults, getDownloadUrl, createPR } from '../services/api';
import SetupProgress from '../components/SetupProgress';
import './ResultsPage.css';

function ResultsPage({ sessionData }) {
  const navigate = useNavigate();
  const sessionId = sessionData?.session_id;
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedFile, setExpandedFile] = useState(null);
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
        <div className="page-two-col">
          <div className="page-left"><SetupProgress currentStep={3} /></div>
          <div className="page-right">
            <div className="empty-state-card">
              <span className="empty-icon">📊</span>
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
              <div className="result-stat-icon">✅</div>
              <div>
                <span className="result-stat-title">Tests Generated</span>
                <span className="result-stat-value">{Object.keys(testFiles).length} test files</span>
              </div>
            </div>
            <div className="result-stat-card info">
              <div className="result-stat-icon">📄</div>
              <div>
                <span className="result-stat-title">Documentation</span>
                <span className="result-stat-value">{Object.keys(docFiles).length} doc files</span>
              </div>
            </div>
            <div className="result-stat-card accent">
              <div className="result-stat-icon">🔥</div>
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
                      <span className="results-file-icon">{file.type === 'test' ? '🧪' : '📄'}</span>
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
                  ⬇ Download All
                </a>
                <button className="ph-btn-primary pr-btn" onClick={() => setShowPR(true)}>
                  🔀 Create Pull Request
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* PR Creation Modal */}
      {showPR && (
        <div className="modal-overlay" onClick={() => setShowPR(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
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
                  <div className="ph-error">{prError}</div>
                )}

                <div className="modal-field">
                  <label>GitHub Personal Access Token</label>
                  <input
                    type="password"
                    className="ph-input"
                    placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                    value={githubToken}
                    onChange={(e) => setGithubToken(e.target.value)}
                  />
                  <span className="ph-hint">Needs 'repo' scope. Token is not stored.</span>
                </div>

                <div className="modal-field">
                  <label>Branch Name</label>
                  <input
                    type="text"
                    className="ph-input"
                    value={branchName}
                    onChange={(e) => setBranchName(e.target.value)}
                  />
                </div>

                <div className="modal-actions">
                  <button className="ph-btn-ghost" onClick={() => setShowPR(false)}>Cancel</button>
                  <button className="ph-btn-primary" onClick={handleCreatePR} disabled={prLoading}>
                    {prLoading ? <span className="spinner" /> : 'Create PR'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultsPage;
