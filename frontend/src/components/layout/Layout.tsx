/**
 * Main layout component.
 * Combines all layout pieces: sidebar, session list, chat.
 */
import { UserButton } from '@clerk/clerk-react';
import { Sidebar } from './Sidebar';
import { SessionList } from './SessionList';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { ThemeToggle } from './ThemeToggle';
import { useAppStore } from '@/store/appStore';
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';

export const Layout: React.FC = () => {
  const { isSidebarOpen, toggleSidebar } = useAppStore();

  return (
    <div className="flex flex-col h-screen">
      {/* Top bar */}
      <header className="h-14 md:h-16 border-b border-border bg-background flex items-center justify-between px-3 md:px-4">
        <div className="flex items-center gap-2 md:gap-4">
          <button
            onClick={toggleSidebar}
            className="p-1.5 md:p-2 rounded-lg hover:bg-accent transition-colors"
            aria-label="Toggle sidebar"
          >
            {isSidebarOpen ? <PanelLeftClose className="w-4 h-4 md:w-5 md:h-5" /> : <PanelLeftOpen className="w-4 h-4 md:w-5 md:h-5" />}
          </button>
          <h1 className="text-lg md:text-xl font-bold">DocGPT</h1>
        </div>

        <div className="flex items-center gap-2 md:gap-4">
          <ThemeToggle />
          <UserButton afterSignOutUrl="/sign-in" />
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar - Documents (hidden on mobile, overlay on tablet) */}
        {isSidebarOpen && (
          <div className="absolute md:relative z-30 md:z-0 w-64 md:w-64 h-full md:h-auto bg-background md:bg-transparent shadow-lg md:shadow-none md:flex-shrink-0">
            <Sidebar />
          </div>
        )}

        {/* Middle sidebar - Sessions (hidden on small mobile) */}
        <div className="hidden sm:block w-48 md:w-64 flex-shrink-0 border-r border-border">
          <SessionList />
        </div>

        {/* Chat area - Full width on mobile */}
        <div className="flex-1 min-w-0">
          <ChatInterface />
        </div>
      </div>
      
      {/* Backdrop for mobile sidebar */}
      {isSidebarOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/50 z-20"
          onClick={toggleSidebar}
        />
      )}
    </div>
  );
};
