import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitContext } from '../services/api';
import './AnalysisPage.css';

function AnalysisPage({ sessionData }) {
  const navigate = useNavigate();
  const [fileContexts, setFileContexts] = useState({});
  const [loading, setLoading] = useState(false);
  const [expandedFile, setExpandedFile] = useState(null);

  if (!sessionData) {
    return (
      <div className="analysis-page animate-fade-in">
        <div className="container">
          <div className="empty-state">
            <span className="empty-icon">📂</span>
            <h2>No Project Loaded</h2>
            <p>Go to Setup to start a new project analysis.</p>
            <button className="btn-primary" onClick={() => navigate('/')}>Go to Setup</button>
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
      <div className="container-wide">
        <div className="page-header">
          <span className="page-subtitle">CODE ANALYSIS</span>
          <h1 className="page-title">Repository Files</h1>
          <p className="page-desc">
            Found <strong>{files.length}</strong> Python files with{' '}
            <strong>{total_functions}</strong> functions ({total_testable} testable).
            Add context below for better test generation.
          </p>
        </div>

        <div className="stats-row">
          <div className="stat-card">
            <span className="stat-value">{files.length}</span>
            <span className="stat-label">Files</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{total_functions}</span>
            <span className="stat-label">Functions</span>
          </div>
          <div className="stat-card accent">
            <span className="stat-value">{total_testable}</span>
            <span className="stat-label">Testable</span>
          </div>
        </div>

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
                  <span className="chip chip-blue">{file.testable_count} testable</span>
                  <span className="chip chip-gray">{file.function_count} functions</span>
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
                          <span className="chip chip-green chip-sm">TESTABLE</span>
                        ) : (
                          <span className="chip chip-amber chip-sm">SKIP</span>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="context-input-section">
                    <label className="context-label">
                      💡 Add context for this file (optional):
                    </label>
                    <textarea
                      className="form-textarea context-textarea"
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

        <div className="action-bar">
          <button className="btn-secondary" onClick={() => navigate('/')}>
            ← Back to Setup
          </button>
          <button
            className={`btn-primary ${loading ? 'loading' : ''}`}
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
                Run Phoenix Pipeline 🔥
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default AnalysisPage;
