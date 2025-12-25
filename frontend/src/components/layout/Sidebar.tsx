/**
 * Sidebar component combining documents and sessions.
 */
import { DocumentUpload } from '@/components/document/DocumentUpload';
import { DocumentList } from './DocumentList';

export const Sidebar: React.FC = () => {
  return (
    <div className="flex flex-col h-full bg-background border-r border-border">
      <DocumentUpload />
      <DocumentList />
    </div>
  );
};
