/**
 * Document upload component.
 * Handles file upload with drag-and-drop support.
 */
import { useState, useRef } from 'react';
import { Upload } from 'lucide-react';
import { useDocuments } from '@/hooks/useDocuments';

export const DocumentUpload: React.FC = () => {
  const { uploadDocument } = useDocuments();
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (file: File) => {
    if (!file.type.includes('pdf')) {
      alert('Only PDF files are allowed');
      return;
    }

    setUploading(true);
    try {
      await uploadDocument(file);
    } catch (err) {
      console.error('Upload failed:', err);
      alert(err instanceof Error ? err.message : 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  return (
    <div className="p-4 border-b border-border">
      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-border hover:border-primary/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleInputChange}
          className="hidden"
        />
        <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
        <p className="text-sm font-medium mb-1">
          {uploading ? 'Uploading...' : 'Upload PDF Document'}
        </p>
        <p className="text-xs text-muted-foreground">
          Click or drag and drop
        </p>
      </div>
    </div>
  );
};
