/**
 * Chat input component.
 * Handles user message input and submission.
 */
import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    const trimmed = message.trim();
    if (!trimmed || disabled) return;

    onSend(trimmed);
    setMessage('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-3 md:p-4 border-t border-border bg-gradient-to-r from-background via-background/95 to-background backdrop-blur-sm">
      <div className="flex gap-2 md:gap-3 items-end">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your document..."
          disabled={disabled}
          className="flex-1 min-h-[50px] md:min-h-[60px] max-h-[150px] md:max-h-[200px] p-3 md:p-4 rounded-xl md:rounded-2xl border-2 border-input bg-background/50 backdrop-blur-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm text-sm md:text-base"
          rows={2}
        />
        <button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          className="p-3 md:p-4 rounded-xl md:rounded-2xl bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
          aria-label="Send message"
        >
          <Send className="w-4 h-4 md:w-5 md:h-5" />
        </button>
      </div>
      <p className="text-xs text-muted-foreground mt-2 ml-1 hidden sm:block">
        💡 Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
};
