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
import { PanelLeftClose, PanelLeftOpen, FileText, MessageSquare } from 'lucide-react';
import { useState } from 'react';

export const Layout: React.FC = () => {
  const { isSidebarOpen, toggleSidebar } = useAppStore();
  const [mobileTab, setMobileTab] = useState<'documents' | 'sessions'>('documents');

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
          <UserButton 
            afterSignOutUrl={`${window.location.origin}/sign-in`}
            appearance={{
              elements: {
                avatarBox: "w-8 h-8 md:w-9 md:h-9"
              }
            }}
          />
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar - Documents (overlay on mobile) */}
        {isSidebarOpen && (
          <div className="absolute md:relative z-30 md:z-0 w-full sm:w-80 md:w-64 h-full md:h-auto bg-background md:bg-transparent shadow-lg md:shadow-none md:flex-shrink-0">
            {/* Mobile tabs - only show on small screens */}
            <div className="sm:hidden flex border-b border-border">
              <button
                onClick={() => setMobileTab('documents')}
                className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${
                  mobileTab === 'documents'
                    ? 'text-foreground border-b-2 border-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <FileText className="w-4 h-4" />
                Documents
              </button>
              <button
                onClick={() => setMobileTab('sessions')}
                className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${
                  mobileTab === 'sessions'
                    ? 'text-foreground border-b-2 border-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                Sessions
              </button>
            </div>

            {/* Mobile content - toggle based on active tab */}
            <div className="sm:hidden h-[calc(100%-49px)]">
              {mobileTab === 'documents' ? <Sidebar /> : <SessionList />}
            </div>

            {/* Desktop content - always show documents */}
            <div className="hidden sm:block h-full">
              <Sidebar />
            </div>
          </div>
        )}

        {/* Middle sidebar - Sessions (visible on sm and up) */}
        <div className="hidden sm:block w-48 md:w-64 flex-shrink-0 border-r border-border">
          <SessionList />
        </div>

        {/* Chat area */}
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
