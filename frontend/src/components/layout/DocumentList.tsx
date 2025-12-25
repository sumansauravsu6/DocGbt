/**
 * Document list sidebar component.
 * Displays all user documents.
 */
import { useEffect } from 'react';
import { FileText, Trash2 } from 'lucide-react';
import { useDocuments } from '@/hooks/useDocuments';
import { useAppStore } from '@/store/appStore';

export const DocumentList: React.FC = () => {
  const { documents, selectedDocument, fetchDocuments, deleteDocument, selectDocument, loading } =
    useDocuments();
  const { setSessions, setMessages } = useAppStore();

  useEffect(() => {
    fetchDocuments();
  }, []);

  // Reselect the persisted document after documents are loaded
  useEffect(() => {
    if (selectedDocument && documents.length > 0) {
      const stillExists = documents.find(d => d.id === selectedDocument.id);
      if (!stillExists) {
        // Document was deleted, clear selection
        selectDocument(null);
      }
    }
  }, [documents]);

  const handleSelectDocument = (doc: typeof documents[0]) => {
    selectDocument(doc);
    setSessions([]);
    setMessages([]);
  };

  const handleDeleteDocument = async (e: React.MouseEvent, docId: string) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument(docId);
      } catch (err) {
        console.error('Failed to delete document:', err);
      }
    }
  };

  if (loading && documents.length === 0) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="text-sm text-muted-foreground">Loading documents...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 md:p-4 border-b border-border">
        <h2 className="text-base md:text-lg font-semibold">Documents</h2>
      </div>

      <div className="flex-1 overflow-y-auto">
        {documents.length === 0 ? (
          <div className="p-3 md:p-4 text-xs md:text-sm text-muted-foreground text-center">
            No documents yet. Upload one to get started.
          </div>
        ) : (
          <div className="p-1.5 md:p-2 space-y-1">
            {documents.map((doc) => (
              <button
                key={doc.id}
                onClick={() => handleSelectDocument(doc)}
                className={`w-full flex items-center gap-2 md:gap-3 p-2 md:p-3 rounded-lg text-left transition-colors group ${
                  selectedDocument?.id === doc.id
                    ? 'bg-accent'
                    : 'hover:bg-accent/50'
                }`}
              >
                <FileText className="w-4 h-4 md:w-5 md:h-5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm md:text-base font-medium truncate">{doc.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {doc.page_count} pages
                  </div>
                </div>
                <button
                  onClick={(e) => handleDeleteDocument(e, doc.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-opacity"
                  aria-label="Delete document"
                >
                  <Trash2 className="w-3 h-3 md:w-4 md:h-4 text-destructive" />
                </button>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
