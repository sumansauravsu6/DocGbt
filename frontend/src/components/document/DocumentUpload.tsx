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
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (file: File) => {
    if (!file.type.includes('pdf')) {
      alert('Only PDF files are allowed');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setFileName(file.name);
    
    try {
      await uploadDocument(file, (progress) => {
        setUploadProgress(progress);
      });
      
      // Reset after successful upload
      setTimeout(() => {
        setUploadProgress(0);
        setFileName('');
      }, 1000);
    } catch (err) {
      console.error('Upload failed:', err);
      alert(err instanceof Error ? err.message : 'Failed to upload document');
      setUploadProgress(0);
      setFileName('');
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
    <div className="p-3 md:p-4 border-b border-border">
      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-2 border-dashed rounded-lg p-4 md:p-6 text-center cursor-pointer transition-colors ${
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
        <Upload className="w-6 h-6 md:w-8 md:h-8 mx-auto mb-2 text-muted-foreground" />
        
        {uploading ? (
          <>
            <p className="text-sm font-medium mb-2">Uploading...</p>
            <p className="text-xs text-muted-foreground mb-3 truncate px-2">{fileName}</p>
            
            {/* Progress bar */}
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            
            {/* Progress percentage */}
            <p className="text-xs font-semibold text-blue-600 dark:text-blue-400">
              {uploadProgress}%
            </p>
          </>
        ) : (
          <>
            <p className="text-sm font-medium mb-1">Upload PDF Document</p>
            <p className="text-xs text-muted-foreground">
              Click or drag and drop
            </p>
          </>
        )}
      </div>
    </div>
  );
};
