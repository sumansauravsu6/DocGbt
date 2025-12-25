/**
 * Session service.
 * Handles all session-related API calls.
 */
import { AxiosInstance } from 'axios';
import { Session, ApiResponse } from '@/types';

export class SessionService {
  constructor(private api: AxiosInstance) {}

  /**
   * Create a new session for a document.
   */
  async createSession(documentId: string, title = 'New Chat'): Promise<Session> {
    const response = await this.api.post<ApiResponse<Session>>(
      `/sessions/document/${documentId}`,
      { title }
    );

    if (!response.data.data) {
      throw new Error('Failed to create session');
    }

    return response.data.data;
  }

  /**
   * Get all sessions for a document.
   */
  async getDocumentSessions(documentId: string, limit = 50, offset = 0): Promise<Session[]> {
    const response = await this.api.get<ApiResponse<{ sessions: Session[] }>>(
      `/sessions/document/${documentId}`,
      {
        params: { limit, offset },
      }
    );

    if (!response.data.data) {
      throw new Error('Failed to fetch sessions');
    }

    return response.data.data.sessions;
  }

  /**
   * Get a specific session by ID.
   */
  async getSession(sessionId: string): Promise<Session> {
    const response = await this.api.get<ApiResponse<Session>>(
      `/sessions/${sessionId}`
    );

    if (!response.data.data) {
      throw new Error('Failed to fetch session');
    }

    return response.data.data;
  }

  /**
   * Update session title.
   */
  async updateSessionTitle(sessionId: string, title: string): Promise<Session> {
    const response = await this.api.patch<ApiResponse<Session>>(
      `/sessions/${sessionId}`,
      { title }
    );

    if (!response.data.data) {
      throw new Error('Failed to update session');
    }

    return response.data.data;
  }

  /**
   * Delete a session.
   */
  async deleteSession(sessionId: string): Promise<void> {
    await this.api.delete(`/sessions/${sessionId}`);
  }
}
