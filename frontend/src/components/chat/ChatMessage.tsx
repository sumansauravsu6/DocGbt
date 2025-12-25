/**
 * Chat message component.
 * Displays a single chat message (user or assistant) with markdown formatting.
 */
import { ChatMessage as ChatMessageType } from '@/types';
import { User, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      {!isUser && (
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-lg">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
      )}

      <div
        className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
            : 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700'
        }`}
      >
        <div className={`prose prose-sm max-w-none break-words ${
          isUser 
            ? 'prose-invert' 
            : 'prose-slate dark:prose-invert'
        }`}>
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              // Custom styling for different markdown elements
              h1: ({...props}) => <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />,
              h2: ({...props}) => <h2 className="text-xl font-bold mt-3 mb-2" {...props} />,
              h3: ({...props}) => <h3 className="text-lg font-semibold mt-2 mb-1" {...props} />,
              p: ({...props}) => <p className="mb-2 leading-relaxed" {...props} />,
              ul: ({...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
              ol: ({...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
              li: ({...props}) => <li className="ml-2" {...props} />,
              code: ({inline, ...props}: any) => 
                inline ? (
                  <code className="bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded text-sm font-mono" {...props} />
                ) : (
                  <code className="block bg-gray-200 dark:bg-gray-700 p-3 rounded-lg text-sm font-mono overflow-x-auto my-2" {...props} />
                ),
              pre: ({...props}) => <pre className="bg-gray-200 dark:bg-gray-700 p-3 rounded-lg overflow-x-auto my-2" {...props} />,
              table: ({...props}) => (
                <div className="overflow-x-auto my-4">
                  <table className="min-w-full border-collapse border border-gray-300 dark:border-gray-600" {...props} />
                </div>
              ),
              thead: ({...props}) => <thead className="bg-gray-200 dark:bg-gray-700" {...props} />,
              th: ({...props}) => <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold" {...props} />,
              td: ({...props}) => <td className="border border-gray-300 dark:border-gray-600 px-4 py-2" {...props} />,
              blockquote: ({...props}) => <blockquote className="border-l-4 border-gray-400 pl-4 italic my-2" {...props} />,
              strong: ({...props}) => <strong className="font-bold" {...props} />,
              em: ({...props}) => <em className="italic" {...props} />,
              a: ({...props}) => <a className="text-blue-500 hover:underline" {...props} />,
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Show sources for assistant messages */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-border/30">
            <div className="text-xs font-semibold mb-2 opacity-70">Sources:</div>
            {message.sources.map((source, idx) => (
              <div key={idx} className="text-xs opacity-70 mb-1">
                Page {source.page_number}
              </div>
            ))}
          </div>
        )}

        <div className="text-xs opacity-70 mt-2">
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>

      {isUser && (
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center flex-shrink-0 shadow-lg">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
};
