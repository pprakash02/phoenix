import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { startProject, getModels } from '../services/api';
import './SetupPage.css';

const SUGGESTION_CHIPS = [
  'SaaS Boilerplate',
  'GraphQL API',
  'Real-time Chat Backend',
];

function SetupPage({ onSessionCreated }) {
  const navigate = useNavigate();
  const [repoUrl, setRepoUrl] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [globalContext, setGlobalContext] = useState('');
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getModels()
      .then((data) => setModels(data.models || []))
      .catch(() => {
        setModels([
          {
            id: 'gpt-4o',
            name: 'GPT OSS 120B',
            description: 'Balanced speed & complex reasoning.',
            configured: true,
            recommended: true,
          },
          {
            id: 'gpt-4o-mini',
            name: 'GPT 4o',
            description: 'Maximum intelligence.',
            configured: true,
            recommended: false,
          },
        ]);
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) {
      setError('Please enter a GitHub repository URL');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await startProject({
        repo_url: repoUrl,
        llm_model: selectedModel,
        global_context: globalContext,
      });
      onSessionCreated(result);
      navigate('/analysis');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (chip) => {
    setGlobalContext((prev) =>
      prev ? `${prev}\n${chip}` : chip
    );
  };

  return (
    <div className="setup-page animate-fade-in">
      <div className="setup-container">
        {/* ─── Left Sidebar ─── */}
        <div className="setup-sidebar">
          <div className="sidebar-badge">
            <span className="badge-dot" />
            Project Setup
          </div>

          <h1 className="sidebar-title">
            Configure your<br />
            <span className="title-highlight">Project Source</span>
          </h1>

          <p className="sidebar-description">
            Provide context and connect your repository.
            Phoenix will analyze your codebase and generate
            complete, production ready test suites and
            documentation.
          </p>

          {/* Progress Steps */}
          <div className="progress-section">
            <h3 className="progress-heading">SETUP PROGRESS</h3>
            <div className="progress-steps">
              <div className="step active">
                <div className="step-number">1</div>
                <div className="step-content">
                  <div className="step-label">Project Details</div>
                  <div className="step-sublabel">Source & AI Context</div>
                </div>
              </div>
              <div className="step-connector" />
              <div className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <div className="step-label">Architecture Review</div>
                  <div className="step-sublabel">Review generated schemas</div>
                </div>
              </div>
              <div className="step-connector" />
              <div className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <div className="step-label">Final Results</div>
                  <div className="step-sublabel">Download and Create PR</div>
                </div>
              </div>
            </div>
          </div>

          {/* Output Preview */}
          <div className="output-section">
            <h3 className="output-heading">Output</h3>
            <div className="output-item">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="8" cy="8" r="6.5"/>
                <path d="M5.5 8L7 9.5L10.5 6" />
              </svg>
              <span>Test Suite for Legacy Functions</span>
            </div>
            <div className="output-item">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="8" cy="8" r="6.5"/>
                <path d="M5.5 8L7 9.5L10.5 6" />
              </svg>
              <span>Documentation for Legacy Codebase</span>
            </div>
          </div>
        </div>

        {/* ─── Right Form Panel ─── */}
        <div className="setup-form-panel">
          <form className="setup-form" onSubmit={handleSubmit}>
            {error && (
              <div className="form-error">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4a.75.75 0 0 1 1.5 0v3a.75.75 0 0 1-1.5 0V5zm.75 6.5a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5z"/>
                </svg>
                {error}
              </div>
            )}

            {/* 1. Project Source */}
            <div className="form-section">
              <h2 className="section-title">1. Project Source</h2>
              <p className="section-subtitle">Connect your repository to sync legacy code.</p>

              <div className="input-with-icon">
                <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.268 2.75 1.026A9.578 9.578 0 0 1 10 4.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.026 2.747-1.026.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C17.137 18.163 20 14.418 20 10c0-5.523-4.477-10-10-10z"/>
                </svg>
                <input
                  id="repo-url-input"
                  type="url"
                  className="form-input"
                  placeholder="https://github.com/username/repository"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  disabled={loading}
                />
              </div>
              <button type="button" className="alt-link">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
                  <path d="M7 0a7 7 0 1 0 0 14A7 7 0 0 0 7 0zM5.5 4.75a1.25 1.25 0 1 1 2.5 0v2a1.25 1.25 0 0 1-2.5 0v-2z"/>
                </svg>
                Use GitLab instead
              </button>
            </div>

            {/* 2. Intelligence Model */}
            <div className="form-section">
              <h2 className="section-title">2. Intelligence Model</h2>
              <p className="section-subtitle">Select the AI engine for code generation.</p>

              <div className="model-cards">
                {models.length > 0 ? models.map((model) => (
                  <label
                    key={model.id}
                    className={`model-card ${selectedModel === model.id ? 'selected' : ''} ${!model.configured ? 'disabled' : ''}`}
                  >
                    <div className="model-card-left">
                      <div className="model-icon">
                        {model.recommended ? (
                          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <rect width="24" height="24" rx="6" fill="#6C5CE7" opacity="0.1"/>
                            <path d="M7 12l3 6 7-12" stroke="#6C5CE7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        ) : (
                          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <rect width="24" height="24" rx="6" fill="#E2E6EF" opacity="0.5"/>
                            <circle cx="12" cy="12" r="4" stroke="#8B949E" strokeWidth="1.5"/>
                          </svg>
                        )}
                      </div>
                      <div className="model-info">
                        <div className="model-name">
                          {model.name}
                          {model.recommended && (
                            <span className="model-badge">RECOMMENDED</span>
                          )}
                        </div>
                        <div className="model-desc">{model.description}</div>
                      </div>
                    </div>
                    <input
                      type="radio"
                      name="model"
                      value={model.id}
                      checked={selectedModel === model.id}
                      onChange={() => setSelectedModel(model.id)}
                      disabled={!model.configured || loading}
                      className="model-radio"
                    />
                  </label>
                )) : (
                  <div className="model-loading">Loading models...</div>
                )}
              </div>
            </div>

            {/* 3. Architecture Context */}
            <div className="form-section">
              <h2 className="section-title">3. Architecture Context</h2>
              <p className="section-subtitle">Describe what you want to build in plain English.</p>

              <div className="textarea-wrapper">
                <textarea
                  id="context-input"
                  className="form-textarea"
                  placeholder="e.g., Build an E-commerce backend with Node js, Express, and PostgreSQL. I need endpoints for products, user authentication (JWT), and a shopping cart. Include a Stripe webhook handler."
                  rows={5}
                  value={globalContext}
                  onChange={(e) => setGlobalContext(e.target.value)}
                  disabled={loading}
                />
                <span className="textarea-hint">Markdown supported</span>
              </div>

              <div className="suggestion-row">
                <span className="suggestion-label">Suggestions:</span>
                {SUGGESTION_CHIPS.map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    className="suggestion-chip"
                    onClick={() => handleSuggestionClick(chip)}
                    disabled={loading}
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="form-footer">
              <button type="button" className="btn-cancel">
                Cancel
              </button>
              <button
                id="start-btn"
                type="submit"
                className={`btn-submit ${loading ? 'loading' : ''}`}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    Generate Backend
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 8h10M9 4l4 4-4 4"/>
                    </svg>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default SetupPage;
