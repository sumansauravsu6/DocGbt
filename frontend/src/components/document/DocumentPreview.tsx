/**
 * Document preview component using PDF.js.
 * Displays PDF document in a viewer.
 */
import { useEffect, useRef, useState } from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';
import { useAppStore } from '@/store/appStore';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

export const DocumentPreview: React.FC = () => {
  const { selectedDocument, toggleDocumentPreview } = useAppStore();
  const canvasRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pageNum, setPageNum] = useState(1);
  const [numPages, setNumPages] = useState(0);
  const pdfDocRef = useRef<any>(null);

  useEffect(() => {
    if (!selectedDocument) return;

    loadPdf();

    return () => {
      if (pdfDocRef.current) {
        pdfDocRef.current.destroy();
      }
    };
  }, [selectedDocument]);

  useEffect(() => {
    if (pdfDocRef.current && pageNum > 0) {
      renderPage(pageNum);
    }
  }, [pageNum]);

  const loadPdf = async () => {
    if (!selectedDocument) return;

    setLoading(true);
    setError(null);

    try {
      const loadingTask = pdfjsLib.getDocument(selectedDocument.file_url);
      const pdf = await loadingTask.promise;

      pdfDocRef.current = pdf;
      setNumPages(pdf.numPages);
      setPageNum(1);
    } catch (err) {
      setError('Failed to load PDF');
      console.error('PDF load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderPage = async (num: number) => {
    if (!pdfDocRef.current || !canvasRef.current) return;

    try {
      const page = await pdfDocRef.current.getPage(num);
      const viewport = page.getViewport({ scale: 1.5 });

      // Clear previous content
      canvasRef.current.innerHTML = '';

      // Create canvas
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');

      if (!context) return;

      canvas.height = viewport.height;
      canvas.width = viewport.width;
      canvas.className = 'pdf-page mx-auto';

      canvasRef.current.appendChild(canvas);

      // Render PDF page
      await page.render({
        canvasContext: context,
        viewport: viewport,
      }).promise;
    } catch (err) {
      console.error('Page render error:', err);
    }
  };

  if (!selectedDocument) {
    return (
      <div className="flex items-center justify-center h-full bg-muted/20">
        <p className="text-muted-foreground">Select a document to preview</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header with Close Button */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div className="flex-1">
          <h3 className="font-semibold truncate">{selectedDocument.name}</h3>
          {numPages > 0 && (
            <div className="flex items-center gap-2 mt-2">
              <button
                onClick={() => setPageNum((prev) => Math.max(1, prev - 1))}
                disabled={pageNum <= 1}
                className="p-1 rounded hover:bg-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Previous page"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-sm min-w-[100px] text-center">
                Page {pageNum} of {numPages}
              </span>
              <button
                onClick={() => setPageNum((prev) => Math.min(numPages, prev + 1))}
                disabled={pageNum >= numPages}
                className="p-1 rounded hover:bg-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Next page"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
        <button
          onClick={toggleDocumentPreview}
          className="p-2 rounded-lg hover:bg-secondary transition-colors ml-4"
          aria-label="Close preview"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* PDF Content */}
      <div className="flex-1 overflow-auto p-4 bg-muted/20">
        {loading && (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">Loading PDF...</p>
          </div>
        )}
        {error && (
          <div className="flex items-center justify-center h-full">
            <p className="text-destructive">{error}</p>
          </div>
        )}
        <div ref={canvasRef} className="pdf-container" />
      </div>
    </div>
  );
};
