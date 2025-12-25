/**
 * Custom hook for session operations.
 */
import { useState, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useAppStore } from '@/store/appStore';
import { createApiClient } from '@/services/api';
import { SessionService } from '@/services/sessionService';
import { Session } from '@/types';

export const useSessions = () => {
  const { getToken } = useAuth();
  const {
    sessions,
    selectedSession,
    setSessions,
    setSelectedSession,
    addSession,
    removeSession,
    updateSessionTitle,
  } = useAppStore();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sessionService = new SessionService(createApiClient(getToken));

  const fetchSessions = useCallback(async (documentId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await sessionService.getDocumentSessions(documentId);
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  const createSession = useCallback(async (documentId: string, title = 'New Chat') => {
    setLoading(true);
    setError(null);
    try {
      const session = await sessionService.createSession(documentId, title);
      addSession(session);
      setSelectedSession(session);
      return session;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create session';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  const deleteSession = useCallback(async (sessionId: string) => {
    setLoading(true);
    setError(null);
    try {
      await sessionService.deleteSession(sessionId);
      removeSession(sessionId);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete session';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  const renameSession = useCallback(async (sessionId: string, title: string) => {
    setLoading(true);
    setError(null);
    try {
      await sessionService.updateSessionTitle(sessionId, title);
      updateSessionTitle(sessionId, title);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to rename session';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  const selectSession = useCallback((session: Session | null) => {
    setSelectedSession(session);
  }, []);

  return {
    sessions,
    selectedSession,
    loading,
    error,
    fetchSessions,
    createSession,
    deleteSession,
    renameSession,
    selectSession,
  };
};
