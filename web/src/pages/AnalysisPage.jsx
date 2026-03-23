import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitContext } from '../services/api';
import SetupProgress from '../components/SetupProgress';
import './AnalysisPage.css';

function AnalysisPage({ sessionData }) {
  const navigate = useNavigate();
  const [fileContexts, setFileContexts] = useState({});
  const [loading, setLoading] = useState(false);
  const [expandedFile, setExpandedFile] = useState(null);

  if (!sessionData) {
    return (
      <div className="analysis-page animate-fade-in">
        <div className="page-two-col">
          <div className="page-left">
            <SetupProgress currentStep={1} />
          </div>
          <div className="page-right">
            <div className="empty-state-card">
              <span className="empty-icon">📂</span>
              <h2>No Project Loaded</h2>
              <p>Go to Setup to start a new project analysis.</p>
              <button className="ph-btn-primary" onClick={() => navigate('/')}>Go to Setup</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const { session_id, files, total_functions, total_testable } = sessionData;

  const handleContextChange = (filePath, value) => {
    setFileContexts((prev) => ({ ...prev, [filePath]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await submitContext(session_id, fileContexts);
      navigate('/progress');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="analysis-page animate-fade-in">
      <div className="page-two-col">
        {/* ─── Left Sidebar ─── */}
        <div className="page-left">
          <div className="sidebar-badge">
            <span className="badge-dot" />
            Code Analysis
          </div>
          <h1 className="sidebar-title">Repository<br /><span>Files</span></h1>
          <p className="sidebar-description">
            Found <strong>{files.length}</strong> Python files with{' '}
            <strong>{total_functions}</strong> functions ({total_testable} testable).
            Add context below for better test generation.
          </p>

          <div className="analysis-stats">
            <div className="mini-stat">
              <span className="mini-stat-value">{files.length}</span>
              <span className="mini-stat-label">Files</span>
            </div>
            <div className="mini-stat">
              <span className="mini-stat-value">{total_functions}</span>
              <span className="mini-stat-label">Functions</span>
            </div>
            <div className="mini-stat accent">
              <span className="mini-stat-value">{total_testable}</span>
              <span className="mini-stat-label">Testable</span>
            </div>
          </div>

          <SetupProgress currentStep={1} />
        </div>

        {/* ─── Right Panel ─── */}
        <div className="page-right">
          <div className="panel-card">
            <div className="file-grid">
              {files.map((file, index) => (
                <div
                  key={file.path}
                  className={`file-card animate-slide-up ${expandedFile === file.path ? 'expanded' : ''}`}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div
                    className="file-card-header"
                    onClick={() => setExpandedFile(expandedFile === file.path ? null : file.path)}
                  >
                    <div className="file-info">
                      <span className="file-icon">📄</span>
                      <div>
                        <span className="file-name">{file.name}</span>
                        <span className="file-path">{file.path}</span>
                      </div>
                    </div>
                    <div className="file-meta">
                      <span className="ph-chip purple">{file.testable_count} testable</span>
                      <span className="ph-chip gray">{file.function_count} functions</span>
                      <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                      <span className="expand-icon">{expandedFile === file.path ? '▲' : '▼'}</span>
                    </div>
                  </div>

                  {expandedFile === file.path && (
                    <div className="file-card-body">
                      <div className="function-list">
                        <h4>Functions:</h4>
                        {file.functions.map((fn) => (
                          <div key={fn.name} className={`function-item ${fn.testable ? '' : 'skipped'}`}>
                            <code>{fn.name}({fn.args.join(', ')})</code>
                            {fn.testable ? (
                              <span className="ph-chip green ph-chip-sm">TESTABLE</span>
                            ) : (
                              <span className="ph-chip amber ph-chip-sm">SKIP</span>
                            )}
                          </div>
                        ))}
                      </div>

                      <div className="context-input-section">
                        <label className="context-label">
                          💡 Add context for this file (optional):
                        </label>
                        <textarea
                          className="ph-textarea"
                          placeholder="e.g., Focus on edge cases for negative numbers, test concurrency behavior..."
                          value={fileContexts[file.path] || ''}
                          onChange={(e) => handleContextChange(file.path, e.target.value)}
                          rows={3}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="panel-footer">
              <button className="ph-btn-ghost" onClick={() => navigate('/')}>
                ← Back to Setup
              </button>
              <button
                className={`ph-btn-primary ${loading ? 'loading' : ''}`}
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" />
                    Starting Pipeline...
                  </>
                ) : (
                  <>
                    Run Phoenix Pipeline
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 8h10M9 4l4 4-4 4"/>
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalysisPage;
