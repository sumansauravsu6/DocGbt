/**
 * Zustand store for global application state.
 * Manages documents, sessions, and UI state.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Document, Session, ChatMessage } from '@/types';

interface AppState {
  // Documents
  documents: Document[];
  selectedDocument: Document | null;
  setDocuments: (documents: Document[]) => void;
  setSelectedDocument: (document: Document | null) => void;
  addDocument: (document: Document) => void;
  removeDocument: (documentId: string) => void;

  // Sessions
  sessions: Session[];
  selectedSession: Session | null;
  setSessions: (sessions: Session[]) => void;
  setSelectedSession: (session: Session | null) => void;
  addSession: (session: Session) => void;
  removeSession: (sessionId: string) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;

  // Messages
  messages: ChatMessage[];
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  addMessages: (messages: ChatMessage[]) => void;
  clearMessages: () => void;

  // UI State
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  
  isDocumentPreviewOpen: boolean;
  toggleDocumentPreview: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
  // Documents
  documents: [],
  selectedDocument: null,
  setDocuments: (documents) =>
    set((state) => {
      // When documents are loaded, if there's a selected session but no selected document,
      // automatically select the document for that session
      if (state.selectedSession && !state.selectedDocument) {
        const document = documents.find(d => d.id === state.selectedSession?.document_id);
        if (document) {
          return { documents, selectedDocument: document };
        }
      }
      return { documents };
    }),
  setSelectedDocument: (selectedDocument) => set({ selectedDocument }),
  addDocument: (document) =>
    set((state) => ({ documents: [document, ...state.documents] })),
  removeDocument: (documentId) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== documentId),
      selectedDocument:
        state.selectedDocument?.id === documentId ? null : state.selectedDocument,
    })),

  // Sessions
  sessions: [],
  selectedSession: null,
  setSessions: (sessions) => set({ sessions }),
  setSelectedSession: (selectedSession) =>
    set((state) => {
      // When selecting a session, ensure the document is also selected
      if (selectedSession && state.selectedDocument?.id !== selectedSession.document_id) {
        const document = state.documents.find(d => d.id === selectedSession.document_id);
        if (document) {
          return { selectedSession, selectedDocument: document };
        }
      }
      return { selectedSession };
    }),
  addSession: (session) =>
    set((state) => ({ sessions: [session, ...state.sessions] })),
  removeSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((sess) => sess.id !== sessionId),
      selectedSession:
        state.selectedSession?.id === sessionId ? null : state.selectedSession,
    })),
  updateSessionTitle: (sessionId, title) =>
    set((state) => ({
      sessions: state.sessions.map((sess) =>
        sess.id === sessionId ? { ...sess, title } : sess
      ),
      selectedSession:
        state.selectedSession?.id === sessionId
          ? { ...state.selectedSession, title }
          : state.selectedSession,
    })),

  // Messages
  messages: [],
  setMessages: (messages) => set({ messages }),
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  addMessages: (messages) =>
    set((state) => ({ messages: [...state.messages, ...messages] })),
  clearMessages: () => set({ messages: [] }),

  // UI State
  theme: (localStorage.getItem('theme') as 'light' | 'dark') || 'light',
  toggleTheme: () =>
    set((state) => {
      const newTheme = state.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', newTheme);
      document.documentElement.classList.toggle('dark', newTheme === 'dark');
      return { theme: newTheme };
    }),
  setTheme: (theme) => {
    localStorage.setItem('theme', theme);
    document.documentElement.classList.toggle('dark', theme === 'dark');
    set({ theme });
  },
  
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  
  isDocumentPreviewOpen: false,  // Changed to false by default
  toggleDocumentPreview: () =>
    set((state) => ({ isDocumentPreviewOpen: !state.isDocumentPreviewOpen })),
}),
    {
      name: 'docgpt-storage',
      partialize: (state) => ({
        selectedDocument: state.selectedDocument,
        selectedSession: state.selectedSession,
        theme: state.theme,
        isSidebarOpen: state.isSidebarOpen,
        isDocumentPreviewOpen: state.isDocumentPreviewOpen,
      }),
    }
  )
);
