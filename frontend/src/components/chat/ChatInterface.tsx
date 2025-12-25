/**
 * Chat interface component.
 * Main chat area with messages and input.
 */
import { useEffect, useRef } from 'react';
import { FileText } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useChat } from '@/hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { DocumentPreview } from '@/components/document/DocumentPreview';

export const ChatInterface: React.FC = () => {
  const { selectedSession, selectedDocument, isDocumentPreviewOpen, toggleDocumentPreview } = useAppStore();
  const { messages, sending, sendMessage, loading } = useChat(selectedSession?.id || null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (message: string) => {
    try {
      await sendMessage(message);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  if (!selectedSession) {
    return (
      <div className="flex items-center justify-center h-full bg-gradient-to-br from-background via-blue-50/30 to-purple-50/30 dark:from-background dark:via-blue-950/20 dark:to-purple-950/20 px-4">
        <div className="text-center animate-in fade-in zoom-in duration-500">
          <div className="w-16 h-16 md:w-20 md:h-20 mx-auto mb-4 md:mb-6 rounded-3xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-2xl">
            <FileText className="w-8 h-8 md:w-10 md:h-10 text-white" />
          </div>
          <h2 className="text-2xl md:text-3xl font-bold mb-2 md:mb-3 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">Welcome to DocGPT</h2>
          <p className="text-sm md:text-base text-muted-foreground max-w-md px-4">
            Your intelligent document assistant powered by AI.<br/>
            Select a document and create a session to start exploring!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-background relative">
      {/* PDF Preview Overlay */}
      {isDocumentPreviewOpen && selectedDocument && (
        <div className="absolute inset-0 z-50 bg-background">
          <DocumentPreview />
        </div>
      )}

      {/* Header */}
      <div className="p-3 md:p-4 border-b border-border bg-gradient-to-r from-background via-purple-50/20 to-blue-50/20 dark:from-background dark:via-purple-950/10 dark:to-blue-950/10 backdrop-blur-sm">
        <div className="flex items-center justify-between gap-2">
          <h2 className="font-semibold text-base md:text-lg truncate">{selectedSession.title}</h2>
          {selectedDocument && (
            <button
              onClick={toggleDocumentPreview}
              className="flex items-center gap-1 md:gap-2 px-2 md:px-4 py-1.5 md:py-2 text-sm md:text-base rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 transition-all shadow-md hover:shadow-lg hover:scale-105 active:scale-95 whitespace-nowrap"
            >
              <FileText className="w-3 h-3 md:w-4 md:h-4" />
              <span className="hidden sm:inline">View PDF</span>
              <span className="sm:hidden">PDF</span>
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loading && messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">Loading messages...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">
              No messages yet. Start a conversation!
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {sending && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 bg-primary-foreground rounded-full animate-pulse" />
                </div>
                <div className="bg-muted rounded-lg p-4">
                  <p className="text-muted-foreground">Thinking...</p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={sending} />
    </div>
  );
};
