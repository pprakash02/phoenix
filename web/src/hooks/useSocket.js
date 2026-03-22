import { useEffect, useRef, useState, useCallback } from 'react';
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:5000';

export function useSocket(sessionId) {
  const socketRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState(null);
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
      }
    });

    socket.on('pipeline_complete', (data) => {
      if (!sessionId || data.session_id === sessionId) {
        setPipelineResult(data);
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

  return { isConnected, progress, pipelineResult, error, joinSession };
}
