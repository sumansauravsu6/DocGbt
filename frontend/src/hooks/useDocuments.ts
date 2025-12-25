/**
 * Custom hook for document operations.
 */
import { useState, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useAppStore } from '@/store/appStore';
import { createApiClient } from '@/services/api';
import { DocumentService } from '@/services/documentService';
import { Document } from '@/types';

export const useDocuments = () => {
  const { getToken } = useAuth();
  const {
    documents,
    selectedDocument,
    sessions,
    selectedSession,
    setDocuments,
    setSelectedDocument,
    addDocument,
    removeDocument,
    setSessions,
    setSelectedSession,
    clearMessages,
  } = useAppStore();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const documentService = new DocumentService(createApiClient(getToken));

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await documentService.getDocuments();
      setDocuments(data.documents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  const uploadDocument = useCallback(async (file: File, onProgress?: (progress: number) => void) => {
    setLoading(true);
    setError(null);
    try {
      const document = await documentService.uploadDocument(file, onProgress);
      addDocument(document);
      return document;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to upload document';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  const deleteDocument = useCallback(async (documentId: string) => {
    // Optimistic update - immediately update UI before backend call
    const deletedDocument = documents.find(doc => doc.id === documentId);
    const deletedSessions = sessions.filter(s => s.document_id === documentId);
    
    // Immediately remove from UI
    removeDocument(documentId);
    
    // Clear selected session if it belongs to this document
    if (selectedSession?.document_id === documentId) {
      setSelectedSession(null);
    }
    
    // Remove all sessions associated with this document
    const remainingSessions = sessions.filter(s => s.document_id !== documentId);
    setSessions(remainingSessions);
    
    // Clear messages from UI
    clearMessages();
    
    // Now call backend in background (don't await, but handle errors)
    setLoading(true);
    setError(null);
    
    documentService.deleteDocument(documentId)
      .catch((err) => {
        // If backend fails, show error but keep UI updated (document already removed)
        const message = err instanceof Error ? err.message : 'Failed to delete document from server';
        setError(message);
        console.error('Backend deletion failed:', message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [getToken, documents, sessions, selectedSession, setSessions, setSelectedSession, clearMessages, removeDocument]);

  const selectDocument = useCallback((document: Document | null) => {
    setSelectedDocument(document);
  }, []);

  return {
    documents,
    selectedDocument,
    loading,
    error,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
    selectDocument,
  };
};
