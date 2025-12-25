/**
 * TypeScript type definitions for DocGPT application.
 */

export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  user_id: string;
  name: string;
  file_url: string;
  file_size: number;
  page_count: number;
  created_at: string;
  updated_at: string;
  sessions?: Session[];
}

export interface Session {
  id: string;
  document_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: ChatMessage[];
  message_count?: number;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: MessageSource[];
  created_at: string;
}

export interface MessageSource {
  page_number: number;
  text: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  error_code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    pages: number;
  };
}
