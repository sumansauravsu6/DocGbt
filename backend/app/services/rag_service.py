"""
RAG (Retrieval Augmented Generation) service.
Handles document-aware chat responses using Groq AI.
"""
from typing import List, Dict
from uuid import UUID
import requests
import json


class RAGService:
    """
    Service for RAG operations using Groq AI.
    """
    
    def __init__(self, vector_service=None):
        self.vector_service = vector_service
        from app.config import Config
        self.groq_api_key = Config.GROQ_API_KEY
        self.groq_model = Config.GROQ_MODEL
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def generate_response(self, query: str, context: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate response using Groq AI with document context and conversation history.
        
        Args:
            query: User question
            context: Relevant document chunks
            conversation_history: Previous messages for context (list of dicts with 'role' and 'content')
            
        Returns:
            Generated response
        """
        try:
            # Build conversation history
            messages = []
            
            # System message with personality and context
            system_prompt = """You are DocGPT, a friendly AI document assistant. Chat naturally like a helpful colleague.

PERSONALITY & BEHAVIOR:
- Respond to greetings warmly and briefly (e.g., "Hi! How can I help you with your document today?")
- Be conversational and natural - avoid overly formal or robotic language
- For simple questions, give simple answers - don't overcomplicate
- Always identify as DocGPT when asked who you are
- You're here to help with documents, but can have casual conversations too

ANSWERING QUESTIONS ABOUT THE DOCUMENT:
- When asked about the document content, provide COMPREHENSIVE and DETAILED answers
- Use ALL the context provided to give a complete picture
- Include specific details, examples, and key points from the document
- If the document covers multiple aspects, mention all of them
- Don't summarize too briefly - give thorough explanations
- Organize your response clearly with sections or bullet points when appropriate

FORMATTING YOUR RESPONSES:
- Use **bold** for important terms, key concepts, or emphasis
- Use *italic* for definitions or subtle emphasis
- Use bullet points (- or *) for lists
- Use numbered lists (1. 2. 3.) for sequential information or steps
- Use tables (markdown format) when comparing multiple items or showing structured data
- Use headings (## or ###) to organize long responses into sections
- Use code blocks (```) for technical content or examples
- Use > for quotes or important notes

IMPORTANT:
- "last message"/"previous one" = the MOST RECENT message in conversation history
- Keep responses concise for greetings, but DETAILED for document content questions
- Don't ask for clarification on simple greetings - just respond warmly
- ALWAYS format your responses using markdown for better readability"""

            if context:
                system_prompt += f"\n\nDocument Content (use when relevant):\n{context}"
            
            messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            if conversation_history and len(conversation_history) > 0:
                for msg in conversation_history[-6:]:  # Last 6 messages
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            # Add current user query
            messages.append({"role": "user", "content": query})
            
            # Call Groq API
            payload = {
                "model": self.groq_model,
                "messages": messages,
                "temperature": 0.1,
                "top_p": 0.85,
                "max_tokens": 2048
            }
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"⏱️ Sending request to Groq AI...")
            response = requests.post(self.groq_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Response received from Groq")
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Groq API error: {str(e)}")
            return f"Error connecting to Groq AI. Error: {str(e)}"
        except Exception as e:
            print(f"❌ Error generating response: {str(e)}")
            return "Sorry, I encountered an error generating a response."
    
    def generate_response_stream(self, query: str, context: str, conversation_history: List[Dict] = None):
        """
        Generate streaming response using Groq AI.
        
        Args:
            query: User question
            context: Relevant document chunks
            conversation_history: Previous messages for context
            
        Yields:
            Generated response chunks
        """
        try:
            # Build messages (same as non-streaming)
            messages = []
            
            system_prompt = """You are DocGPT, a friendly AI document assistant. Chat naturally like a helpful colleague.

PERSONALITY & BEHAVIOR:
- Respond to greetings warmly and briefly
- Be conversational and natural
- For simple questions, give simple answers
- Always identify as DocGPT when asked who you are

ANSWERING QUESTIONS ABOUT THE DOCUMENT:
- When asked about the document, provide COMPREHENSIVE and DETAILED answers
- Use ALL the context to give a complete picture
- Include specific details and key points
- Don't summarize too briefly - give thorough explanations

FORMATTING YOUR RESPONSES:
- Use **bold** for important terms and key concepts
- Use *italic* for definitions or subtle emphasis
- Use bullet points for lists
- Use numbered lists for sequential information
- Use tables (markdown) when comparing items
- Use headings (##) to organize sections
- ALWAYS format responses using markdown

IMPORTANT:
- "last message"/"previous one" = the MOST RECENT message in conversation history
- Keep responses concise for greetings, but DETAILED for document content questions"""

            if context:
                system_prompt += f"\n\nDocument Content:\n{context}"
            
            messages.append({"role": "system", "content": system_prompt})
            
            if conversation_history and len(conversation_history) > 0:
                for msg in conversation_history[-6:]:
                    messages.append({"role": msg['role'], "content": msg['content']})
            
            messages.append({"role": "user", "content": query})
            
            # Call Groq API with streaming
            payload = {
                "model": self.groq_model,
                "messages": messages,
                "temperature": 0.1,
                "top_p": 0.85,
                "max_tokens": 2048,
                "stream": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"⏱️ Starting streaming request to Groq AI...")
            response = requests.post(self.groq_url, json=payload, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
            
            print(f"✅ Streaming complete")
            
        except Exception as e:
            print(f"❌ Error in streaming: {str(e)}")
            yield "Sorry, I encountered an error generating a response."
    
    def retrieve_context(self, query: str, document_id: UUID, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant chunks from document.
        
        Args:
            query: User query
            document_id: Document to search
            top_k: Number of chunks to retrieve (default reduced to 3 for speed)
            
        Returns:
            List of relevant chunks with metadata
        """
        return self.vector_service.search(query, document_id, top_k)
    
    def generate_answer(self, query: str, context_chunks: List[Dict], 
                       conversation_history: List[Dict] = None) -> Dict:
        """
        Generate answer based on retrieved context.
        
        IMPORTANT: This is a free-tier implementation using only retrieval.
        For production with LLM, integrate Hugging Face models or similar.
        
        Args:
            query: User query
            context_chunks: Retrieved document chunks
            conversation_history: Previous messages for context
            
        Returns:
            Dict with answer and sources
        """
        # Check if we have relevant context
        if not context_chunks:
            return {
                'answer': "The requested information is not available in this document.",
                'sources': []
            }
        
        # Simple implementation: return most relevant chunks
        # In production, use an LLM to generate natural language response
        
        # Extract unique page numbers
        pages = sorted(set(chunk['page_number'] for chunk in context_chunks))
        
        # Format sources
        sources = [
            {
                'page_number': chunk['page_number'],
                'text': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
            }
            for chunk in context_chunks[:3]  # Top 3 chunks
        ]
        
        # Generate simple answer
        # NOTE: Replace this with actual LLM integration
        answer_parts = []
        answer_parts.append(f"Based on the document (pages {', '.join(map(str, pages))}):\n")
        
        for i, chunk in enumerate(context_chunks[:2], 1):
            answer_parts.append(f"\n{i}. {chunk['text'][:300]}...")
        
        answer = ''.join(answer_parts)
        
        return {
            'answer': answer,
            'sources': sources
        }
    
    def chat(self, query: str, document_id: UUID, conversation_history: List[Dict] = None) -> Dict:
        """
        Main chat method combining retrieval and generation.
        
        Args:
            query: User query
            document_id: Document to chat about
            conversation_history: Previous messages
            
        Returns:
            Dict with answer and sources
        """
        # Retrieve relevant context
        context_chunks = self.retrieve_context(query, document_id, top_k=5)
        
        # Generate answer
        result = self.generate_answer(query, context_chunks, conversation_history)
        
        return result
    
    def format_conversation_history(self, messages: List[Dict]) -> List[Dict]:
        """
        Format conversation history for context.
        
        Args:
            messages: List of message dicts
            
        Returns:
            Formatted conversation history
        """
        return [
            {
                'role': msg['role'],
                'content': msg['content']
            }
            for msg in messages[-10:]  # Last 10 messages for context
        ]
