"""
Vector service for Qdrant cloud operations.
Handles embedding storage and retrieval.
"""
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict
from app.config import Config
from uuid import UUID


class VectorService:
    """
    Service for vector database operations using Qdrant.
    
    Handles document embeddings and semantic search.
    """
    
    def __init__(self):
        """Initialize Qdrant client and Jina AI configuration."""
        # Jina AI configuration
        self.jina_api_key = Config.JINA_API_KEY
        self.jina_model = Config.JINA_MODEL
        self.vector_size = Config.EMBEDDING_VECTOR_SIZE
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY,
            timeout=60
        )
        
        self.collection_name = Config.QDRANT_COLLECTION_NAME
        
        # Check if collection exists and create if needed
        try:
            from qdrant_client.models import PayloadSchemaType
            
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)
            
            if collection_exists:
                # Check if vector size matches
                collection_info = self.client.get_collection(self.collection_name)
                existing_vector_size = collection_info.config.params.vectors.size
                
                if existing_vector_size != self.vector_size:
                    print(f"⚠️ Vector dimension mismatch! Expected {self.vector_size}, got {existing_vector_size}")
                    print(f"🔄 Recreating collection with correct dimensions...")
                    # Delete old collection
                    self.client.delete_collection(self.collection_name)
                    # Create new collection with correct dimensions
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
                    )
                    # Create index for document_id
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="document_id",
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                    print(f"✅ Recreated Qdrant collection with {self.vector_size} dimensions")
                else:
                    print(f"✅ Connected to existing Qdrant collection: {self.collection_name}")
                    # Create index for document_id if it doesn't exist (improves filter performance)
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name="document_id",
                            field_schema=PayloadSchemaType.KEYWORD
                        )
                        print(f"✅ Created payload index for document_id")
                    except Exception:
                        pass  # Index might already exist
            else:
                # Create new collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
                )
                # Create index for document_id
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                print(f"✅ Created new Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"⚠️ Warning: Could not verify/create collection: {str(e)}")
        
        print(f"✅ VectorService initialized with Jina AI model: {self.jina_model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Jina AI API.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing embedding vector
        """
        url = "https://api.jina.ai/v1/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jina_api_key}"
        }
        data = {
            "model": self.jina_model,
            "input": [text]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['data'][0]['embedding']
        except Exception as e:
            print(f"❌ Error generating embedding: {str(e)}")
            raise
    
    def add_document_chunks(self, document_id: UUID, chunks: List[Dict[str, any]]):
        """
        Add document chunks to vector database.
        
        Args:
            document_id: UUID of parent document
            chunks: List of chunk dicts with page_number, chunk_id, text
            
        Example chunks format:
            [
                {'page_number': 1, 'chunk_id': 0, 'text': 'Chunk text...'},
                {'page_number': 1, 'chunk_id': 1, 'text': 'More text...'},
            ]
        """
        if not chunks:
            return
        
        # Prepare points for Qdrant
        points = []
        
        for idx, chunk in enumerate(chunks):
            # Generate unique ID for chunk
            chunk_id = f"{document_id}_page{chunk['page_number']}_chunk{chunk['chunk_id']}"
            
            # Generate embedding
            embedding = self.generate_embedding(chunk['text'])
            
            # Create point with payload
            point = PointStruct(
                id=hash(chunk_id) % (2**63),  # Convert string ID to int
                vector=embedding,
                payload={
                    'chunk_id': chunk_id,
                    'document_id': str(document_id),
                    'page_number': chunk['page_number'],
                    'chunk_number': chunk['chunk_id'],
                    'text': chunk['text']
                }
            )
            points.append(point)
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        print(f"✅ Added {len(chunks)} chunks for document {document_id}")
    
    def search(self, query: str, document_id: UUID, top_k: int = 5) -> List[Dict[str, any]]:
        """
        Semantic search within a specific document.
        
        Args:
            query: Search query
            document_id: UUID of document to search within
            top_k: Number of results to return
            
        Returns:
            List of matching chunks with metadata
            
        Format:
            [
                {
                    'text': 'Chunk text...',
                    'page_number': 1,
                    'chunk_id': 0,
                    'distance': 0.15
                },
                ...
            ]
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Search with document_id filter
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=str(document_id))
                    )
                ]
            ),
            limit=top_k
        )
        
        # Format results
        formatted_results = []
        for scored_point in search_result:
            formatted_results.append({
                'text': scored_point.payload.get('text', ''),
                'page_number': scored_point.payload.get('page_number', 0),
                'chunk_id': scored_point.payload.get('chunk_number', 0),
                'distance': 1 - scored_point.score  # Convert cosine similarity to distance
            })
        
        return formatted_results
    
    def delete_document_chunks(self, document_id: UUID):
        """
        Delete all chunks for a document.
        Called when document is deleted.
        
        Args:
            document_id: UUID of document
        """
        try:
            # Delete all points with matching document_id
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=str(document_id))
                        )
                    ]
                )
            )
            
            print(f"✅ Deleted chunks for document {document_id}")
        
        except Exception as e:
            print(f"❌ Error deleting chunks: {str(e)}")
    
    def get_chunk_count(self, document_id: UUID) -> int:
        """Get number of chunks for a document."""
        try:
            # Count points with matching document_id
            count_result = self.client.count(
                collection_name=self.collection_name,
                count_filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=str(document_id))
                        )
                    ]
                )
            )
            return count_result.count
        except Exception:
            return 0
