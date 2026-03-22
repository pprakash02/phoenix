const API_BASE = 'http://localhost:5000/api';

export async function startProject(data) {
  const res = await fetch(`${API_BASE}/start-project`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to start project');
  }
  return res.json();
}

export async function submitContext(sessionId, fileContexts) {
  const res = await fetch(`${API_BASE}/submit-context`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, file_contexts: fileContexts }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to submit context');
  }
  return res.json();
}

export async function getModels() {
  const res = await fetch(`${API_BASE}/models`);
  return res.json();
}

export async function getSession(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  return res.json();
}

export async function approveTests(sessionId) {
  const res = await fetch(`${API_BASE}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  });
  return res.json();
}

export async function rejectTests(sessionId, comments) {
  const res = await fetch(`${API_BASE}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, comments }),
  });
  return res.json();
}

export async function getResults(sessionId) {
  const res = await fetch(`${API_BASE}/results/${sessionId}`);
  return res.json();
}

export function getDownloadUrl(sessionId) {
  return `${API_BASE}/download/${sessionId}`;
}

export async function createPR(sessionId, githubToken, branchName) {
  const res = await fetch(`${API_BASE}/create-pr`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      github_token: githubToken,
      branch_name: branchName,
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to create PR');
  }
  return res.json();
}
