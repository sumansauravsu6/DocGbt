/**
 * Document page - shows specific document and its sessions.
 */
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { useDocuments } from '@/hooks/useDocuments';

export const DocumentPage: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const { documents, selectDocument } = useDocuments();

  useEffect(() => {
    if (!documentId) {
      navigate('/');
      return;
    }

    // Find and select document
    const doc = documents.find((d) => d.id === documentId);
    if (doc) {
      selectDocument(doc);
    }
  }, [documentId, documents]);

  return <Layout />;
};
