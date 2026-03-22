import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { startProject, getModels } from '../services/api';
import './SetupPage.css';

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
          { id: 'gpt-4o', name: 'GPT-4o', description: 'OpenAI flagship model', configured: true },
          { id: 'claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', description: 'Anthropic Claude', configured: false },
          { id: 'mistral-large', name: 'Mistral Large', description: 'Mistral AI', configured: false },
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

  return (
    <div className="setup-page animate-fade-in">
      <div className="container">
        <div className="page-header">
          <span className="page-subtitle">ARCHITECTURE CONFIGURATION</span>
          <h1 className="page-title">Setup Project</h1>
        </div>

        <form className="setup-form" onSubmit={handleSubmit}>
          {error && (
            <div className="form-error">
              <span className="error-icon">⚠</span>
              {error}
            </div>
          )}

          <div className="form-section">
            <label className="form-label">
              <span className="label-icon">📦</span>
              GIT REPOSITORY URL
            </label>
            <input
              id="repo-url-input"
              type="url"
              className="form-input"
              placeholder="https://github.com/organization/repository"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              disabled={loading}
            />
            <p className="form-help">Clone via HTTPS or SSH. Ensure 'Phoenix' has read access.</p>
          </div>

          <div className="form-section">
            <label className="form-label">
              <span className="label-icon">🤖</span>
              LLM SELECTION
            </label>
            <select
              id="llm-select"
              className="form-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={loading}
            >
              {models.map((model) => (
                <option key={model.id} value={model.id} disabled={!model.configured}>
                  {model.name}{!model.configured ? ' (Not configured)' : ''}
                </option>
              ))}
            </select>
            <p className="form-help">Select the core model to drive the architectural reasoning and code generation.</p>
          </div>

          <div className="form-section">
            <label className="form-label">
              <span className="label-icon">💡</span>
              AI AGENT CONTEXT
            </label>
            <textarea
              id="context-input"
              className="form-textarea"
              placeholder="Describe the business logic, architectural constraints, and preferred tech stack..."
              rows={5}
              value={globalContext}
              onChange={(e) => setGlobalContext(e.target.value)}
              disabled={loading}
            />
            <p className="form-help">Provide high-level instructions to guide the automated backend generation.</p>
          </div>

          <button
            id="start-btn"
            type="submit"
            className={`form-submit ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Cloning & Analyzing...
              </>
            ) : (
              <>
                Start Project Backend
                <span className="submit-icon">🚀</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default SetupPage;
