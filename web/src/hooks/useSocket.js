import { useEffect, useRef, useState, useCallback } from 'react';
import { io } from 'socket.io-client';

const SOCKET_URL = window.location.origin;

// localStorage keys for pipeline state
const KEY_PROGRESS = 'phoenix_socketProgress';
const KEY_RESULT = 'phoenix_socketResult';
const KEY_STAGES = 'phoenix_progressStages';
const KEY_MAX_PROGRESS = 'phoenix_maxProgress';

const ALL_PIPELINE_KEYS = [KEY_PROGRESS, KEY_RESULT, KEY_STAGES, KEY_MAX_PROGRESS];

/**
 * Clear all pipeline-related localStorage keys.
 * Exported so AnalysisPage can call it before starting a new pipeline.
 */
export function clearAllPipelineState() {
  ALL_PIPELINE_KEYS.forEach((key) => {
    try { localStorage.removeItem(key); } catch {}
  });
}

function safeParse(key) {
  try {
    const v = localStorage.getItem(key);
    return v ? JSON.parse(v) : null;
  } catch { return null; }
}

export function useSocket(sessionId) {
  const socketRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);

  // Restore progress from localStorage (so tab-switching preserves the timeline),
  // but NEVER restore pipelineResult — that must come from a live WebSocket event only.
  const [progress, setProgress] = useState(() => safeParse(KEY_PROGRESS));
  const [pipelineResult, setPipelineResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const socket = io(SOCKET_URL, {
      transports: ['polling', 'websocket'],
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      if (sessionId) {
        socket.emit('join_session', { session_id: sessionId });
      }
    });

    socket.on('disconnect', () => setIsConnected(false));

    socket.on('agent_progress', (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setProgress(data);
        try { localStorage.setItem(KEY_PROGRESS, JSON.stringify(data)); } catch {}
      }
    });

    socket.on('pipeline_complete', (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setPipelineResult(data);
        // Don't persist pipelineResult — it must only come from live events
      }
    });

    socket.on('pipeline_error', (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setError(data.error || 'Pipeline failed');
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [sessionId]);

  const joinSession = useCallback((sid) => {
    if (socketRef.current) {
      socketRef.current.emit('join_session', { session_id: sid });
    }
  }, []);

  const resetState = useCallback(() => {
    clearAllPipelineState();
    setProgress(null);
    setPipelineResult(null);
    setError(null);
  }, []);

  return { isConnected, progress, pipelineResult, error, joinSession, resetState };
}
