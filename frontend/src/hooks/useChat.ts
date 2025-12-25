/**
 * Custom hook for chat operations.
 */
import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useAppStore } from '@/store/appStore';
import { createApiClient } from '@/services/api';
import { ChatService } from '@/services/chatService';

export const useChat = (sessionId: string | null) => {
  const { getToken } = useAuth();
  const { messages, setMessages, addMessage, clearMessages } = useAppStore();

  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const chatService = new ChatService(createApiClient(getToken));

  const fetchMessages = useCallback(async () => {
    if (!sessionId) {
      clearMessages();
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await chatService.getMessages(sessionId);
      setMessages(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch messages');
    } finally {
      setLoading(false);
    }
  }, [sessionId, getToken]);

  const sendMessage = useCallback(async (message: string) => {
    if (!sessionId) {
      throw new Error('No session selected');
    }

    setSending(true);
    setError(null);
    
    // Add user message immediately to UI
    const tempUserMessage = {
      id: `temp-user-${Date.now()}`,
      session_id: sessionId,
      role: 'user' as const,
      content: message,
      created_at: new Date().toISOString(),
    };
    addMessage(tempUserMessage);
    
    // Add temporary assistant message for streaming
    const tempAssistantMessage = {
      id: `temp-assistant-${Date.now()}`,
      session_id: sessionId,
      role: 'assistant' as const,
      content: '',
      created_at: new Date().toISOString(),
    };
    addMessage(tempAssistantMessage);
    
    try {
      await chatService.sendMessageStream(
        sessionId,
        message,
        getToken,
        // On chunk received
        (chunk: string) => {
          const currentMessages = useAppStore.getState().messages;
          const updatedMessages = currentMessages.map(m => 
            m.id === tempAssistantMessage.id 
              ? { ...m, content: m.content + chunk }
              : m
          );
          setMessages(updatedMessages);
        },
        // On complete
        (userMsg: any, assistantMsg: any) => {
          // Just update the IDs and final data without removing messages
          const currentMessages = useAppStore.getState().messages;
          const updatedMessages = currentMessages.map(m => {
            if (m.id === tempUserMessage.id) {
              return { ...m, id: userMsg.id || m.id };
            }
            if (m.id === tempAssistantMessage.id) {
              return { ...assistantMsg };
            }
            return m;
          });
          setMessages(updatedMessages);
          setSending(false);
        },
        // On error
        (errorMsg: string) => {
          const currentMessages = useAppStore.getState().messages;
          setMessages(currentMessages.filter(m => m.id !== tempUserMessage.id && m.id !== tempAssistantMessage.id));
          setError(errorMsg);
          setSending(false);
          throw new Error(errorMsg);
        }
      );
    } catch (err) {
      // Error already handled in onError callback
      console.error('Failed to send message:', err);
    }
  }, [sessionId, getToken]);

  const clearHistory = useCallback(async () => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);
    try {
      await chatService.clearSessionHistory(sessionId);
      clearMessages();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to clear history';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [sessionId, getToken]);

  // Fetch messages when session changes
  useEffect(() => {
    fetchMessages();
  }, [sessionId]);

  return {
    messages,
    loading,
    sending,
    error,
    sendMessage,
    fetchMessages,
    clearHistory,
  };
};
