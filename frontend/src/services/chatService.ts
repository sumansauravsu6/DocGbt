/**
 * Chat service.
 * Handles all chat-related API calls.
 */
import { AxiosInstance } from 'axios';
import { ChatMessage, ApiResponse } from '@/types';

export class ChatService {
  constructor(private api: AxiosInstance) {}

  /**
   * Send a message and get AI response with streaming.
   */
  async sendMessageStream(
    sessionId: string,
    message: string,
    getToken: () => Promise<string | null>,
    onChunk: (chunk: string) => void,
    onComplete: (userMessage: ChatMessage, assistantMessage: ChatMessage) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('No authentication token');
      }
      
      const baseURL = this.api.defaults.baseURL || 'http://localhost:5000/api';
      const url = `${baseURL}/chat/sessions/${sessionId}/messages`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';
      let assistantContent = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.chunk) {
              assistantContent += data.chunk;
              onChunk(data.chunk);
            } else if (data.done && data.message) {
              // Get user message (should be in previous response or create temp)
              const tempUserMessage: ChatMessage = {
                id: `temp-${Date.now()}`,
                session_id: sessionId,
                role: 'user',
                content: message,
                created_at: new Date().toISOString(),
              };
              onComplete(tempUserMessage, data.message);
            } else if (data.error) {
              onError(data.error);
            }
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to send message');
    }
  }

  /**
   * Send a message and get AI response.
   */
  async sendMessage(
    sessionId: string,
    message: string
  ): Promise<{ user_message: ChatMessage; assistant_message: ChatMessage }> {
    const response = await this.api.post<
      ApiResponse<{ user_message: ChatMessage; assistant_message: ChatMessage }>
    >(`/chat/sessions/${sessionId}/messages`, { message });

    if (!response.data.data) {
      throw new Error('Failed to send message');
    }

    return response.data.data;
  }

  /**
   * Get all messages for a session.
   */
  async getMessages(sessionId: string, limit = 100, offset = 0): Promise<ChatMessage[]> {
    const response = await this.api.get<ApiResponse<{ messages: ChatMessage[] }>>(
      `/chat/sessions/${sessionId}/messages`,
      {
        params: { limit, offset },
      }
    );

    if (!response.data.data) {
      throw new Error('Failed to fetch messages');
    }

    return response.data.data.messages;
  }

  /**
   * Clear all messages in a session.
   */
  async clearSessionHistory(sessionId: string): Promise<void> {
    await this.api.delete(`/chat/sessions/${sessionId}/clear`);
  }
}
