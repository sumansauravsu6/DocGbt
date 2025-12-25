/**
 * Document service.
 * Handles all document-related API calls.
 */
import { AxiosInstance } from 'axios';
import { Document, ApiResponse } from '@/types';

export class DocumentService {
  constructor(private api: AxiosInstance) {}

  /**
   * Upload a new document.
   */
  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post<ApiResponse<Document>>(
      '/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    if (!response.data.data) {
      throw new Error('Failed to upload document');
    }

    return response.data.data;
  }

  /**
   * Get all documents for current user.
   */
  async getDocuments(limit = 100, offset = 0): Promise<{ documents: Document[]; total: number }> {
    const response = await this.api.get<ApiResponse<{ documents: Document[]; total: number }>>(
      '/documents',
      {
        params: { limit, offset },
      }
    );

    if (!response.data.data) {
      throw new Error('Failed to fetch documents');
    }

    return response.data.data;
  }

  /**
   * Get a specific document by ID.
   */
  async getDocument(documentId: string): Promise<Document> {
    const response = await this.api.get<ApiResponse<Document>>(
      `/documents/${documentId}`
    );

    if (!response.data.data) {
      throw new Error('Failed to fetch document');
    }

    return response.data.data;
  }

  /**
   * Delete a document.
   */
  async deleteDocument(documentId: string): Promise<void> {
    await this.api.delete(`/documents/${documentId}`);
  }
}
