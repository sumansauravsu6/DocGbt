/**
 * Session list sidebar component.
 * Displays all sessions for the selected document.
 */
import { useEffect } from 'react';
import { MessageSquare, Trash2, Plus } from 'lucide-react';
import { useSessions } from '@/hooks/useSessions';
import { useAppStore } from '@/store/appStore';

export const SessionList: React.FC = () => {
  const { selectedDocument } = useAppStore();
  const { sessions, selectedSession, fetchSessions, createSession, deleteSession, selectSession, loading } =
    useSessions();

  useEffect(() => {
    if (selectedDocument) {
      fetchSessions(selectedDocument.id);
    }
  }, [selectedDocument]);

  // Reselect the persisted session after sessions are loaded
  useEffect(() => {
    if (selectedSession && sessions.length > 0) {
      const stillExists = sessions.find(s => s.id === selectedSession.id);
      if (!stillExists) {
        // Session was deleted, clear selection
        selectSession(null);
      }
    }
  }, [sessions]);

  const handleCreateSession = async () => {
    if (!selectedDocument) return;
    try {
      await createSession(selectedDocument.id);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this session?')) {
      try {
        await deleteSession(sessionId);
      } catch (err) {
        console.error('Failed to delete session:', err);
      }
    }
  };

  if (!selectedDocument) {
    return (
      <div className="flex items-center justify-center p-4 h-full">
        <div className="text-sm text-muted-foreground text-center">
          Select a document to view sessions
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h2 className="text-lg font-semibold">Sessions</h2>
        <button
          onClick={handleCreateSession}
          className="p-2 rounded-lg hover:bg-accent transition-colors"
          aria-label="New session"
        >
          <Plus className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading && sessions.length === 0 ? (
          <div className="p-4 text-sm text-muted-foreground text-center">
            Loading sessions...
          </div>
        ) : sessions.length === 0 ? (
          <div className="p-4 text-sm text-muted-foreground text-center">
            No sessions yet. Create one to start chatting.
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => selectSession(session)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors group ${
                  selectedSession?.id === session.id
                    ? 'bg-accent'
                    : 'hover:bg-accent/50'
                }`}
              >
                <MessageSquare className="w-5 h-5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{session.title}</div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(session.created_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(e, session.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-opacity"
                  aria-label="Delete session"
                >
                  <Trash2 className="w-4 h-4 text-destructive" />
                </button>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
