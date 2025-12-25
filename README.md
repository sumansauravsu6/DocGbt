# DocGPT - AI-Powered Document Chat Platform

A production-ready, document-centric AI chat platform where each uploaded document becomes its own dedicated GPT-like assistant. Built with free-tier services and open-source technologies.

## 🎯 Features

- **Document-Centric Chat**: Each uploaded PDF becomes a dedicated AI assistant
- **Multiple Sessions**: Create isolated chat sessions per document (like ChatGPT's "New Chat")
- **Secure Authentication**: Clerk-based authentication with JWT verification
- **RAG Architecture**: Retrieval-Augmented Generation for accurate, document-based answers
- **PDF Preview**: Built-in PDF viewer with page navigation
- **Dark/Light Mode**: Fully customizable theme with persistence
- **Responsive UI**: Clean, modern interface built with Tailwind CSS
- **Cloud-First**: Supabase for database and file storage
- **Vector Search**: ChromaDB for semantic search and embeddings

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS (dark/light mode)
- Clerk React SDK (authentication)
- PDF.js (document preview)
- Zustand (state management)
- Axios (HTTP client)
- Vite (build tool)

**Backend:**
- Python 3.10+ with Flask
- Flask Blueprints (modular routing)
- SQLAlchemy ORM
- Supabase (PostgreSQL database + file storage)
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- PyPDF2 (PDF processing)

### Project Structure

```
docGbt/
├── backend/                    # Flask backend
│   ├── app/
│   │   ├── __init__.py        # App factory
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database setup
│   │   ├── middleware/        # Auth middleware
│   │   ├── models/            # SQLAlchemy models
│   │   ├── repositories/      # Data access layer
│   │   ├── services/          # Business logic
│   │   ├── routes/            # Flask blueprints
│   │   └── utils/             # Utilities
│   ├── migrations/            # SQL schema
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Entry point
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Route pages
│   │   ├── services/          # API layer
│   │   ├── hooks/             # Custom hooks
│   │   ├── store/             # Zustand store
│   │   ├── types/             # TypeScript types
│   │   └── main.tsx           # Entry point
│   └── package.json           # npm dependencies
└── docker/                     # Docker configs
    └── docker-compose.yml     # ChromaDB container
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for ChromaDB)
- Supabase account (free tier)
- Clerk account (free tier)

### 1. Database Setup (Supabase)

1. Create a new Supabase project at https://supabase.com
2. Go to SQL Editor and run the schema from `backend/migrations/supabase_schema.sql`
3. Create a storage bucket named `documents` in Storage section
4. Note your project URL and API keys

### 2. Authentication Setup (Clerk)

1. Create a new application at https://clerk.com
2. Enable email/password authentication
3. Note your publishable key and secret key

### 3. Vector Database Setup (ChromaDB)

Start ChromaDB using Docker:

```bash
cd docker
docker-compose up -d
```

This starts ChromaDB on `http://localhost:8000`

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
# - SUPABASE_SERVICE_KEY
# - CLERK_SECRET_KEY
# - etc.

# Run the server
python run.py
```

Backend will start on `http://localhost:5000`

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your Clerk publishable key:
# VITE_CLERK_PUBLISHABLE_KEY=pk_test_...

# Start development server
npm run dev
```

Frontend will start on `http://localhost:5173`

## 📡 API Endpoints

### Authentication
- `GET /api/auth/me` - Get current user
- `GET /api/auth/status` - Check auth status

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - Get all documents
- `GET /api/documents/<id>` - Get specific document
- `DELETE /api/documents/<id>` - Delete document

### Sessions
- `POST /api/sessions/document/<document_id>` - Create session
- `GET /api/sessions/document/<document_id>` - Get document sessions
- `GET /api/sessions/<id>` - Get specific session
- `PATCH /api/sessions/<id>` - Update session title
- `DELETE /api/sessions/<id>` - Delete session

### Chat
- `POST /api/chat/sessions/<session_id>/messages` - Send message
- `GET /api/chat/sessions/<session_id>/messages` - Get messages
- `DELETE /api/chat/sessions/<session_id>/clear` - Clear history

## 🔒 Security

- **Authentication**: Clerk JWT tokens verified on every request
- **Authorization**: Row-level security in Supabase
- **File Upload**: Validated file types (PDF only)
- **Data Isolation**: Users can only access their own documents
- **CORS**: Configured for specific origins
- **Environment Variables**: Sensitive data in .env files

## 🎨 UI Features

### Layout
- **Left Sidebar**: Document list with upload
- **Middle Sidebar**: Session list for selected document
- **Main Area**: Chat interface
- **Right Panel**: PDF preview with pagination

### Interactions
- Drag-and-drop file upload
- Real-time chat updates
- Auto-scroll to latest messages
- Session title auto-generation
- Theme persistence in localStorage
- Responsive sidebar toggles

## 🧠 RAG Implementation

The AI response generation follows strict RAG principles:

1. **Vector Search**: User query → embedding → semantic search in document chunks
2. **Context Retrieval**: Top-K relevant chunks filtered by document_id
3. **Answer Generation**: Response based ONLY on retrieved chunks
4. **Source Attribution**: Page numbers included in responses
5. **Fallback**: "Information not available" if no relevant chunks found

### Free-Tier Note

The current implementation uses basic retrieval without a language model. For production:

- Integrate Hugging Face models (free)
- Use local LLMs (Ollama, llama.cpp)
- Or switch to paid APIs (OpenAI, Anthropic)

Simply update `app/services/rag_service.py` → `generate_answer()` method.

## 📦 Deployment

### Backend (Render/Railway/Heroku)

1. Set environment variables
2. Update `SUPABASE_URL` with production URL
3. Deploy using `requirements.txt`
4. Set start command: `gunicorn run:app`

### Frontend (Vercel/Netlify)

1. Set `VITE_CLERK_PUBLISHABLE_KEY`
2. Set `VITE_API_URL` to backend URL
3. Deploy from GitHub
4. Build command: `npm run build`
5. Output directory: `dist`

### ChromaDB (Persistent Storage)

For production, either:
- Use ChromaDB Cloud (when available)
- Deploy ChromaDB on VPS with Docker
- Switch to Qdrant (free tier available)

## 🛠️ Development

### Code Organization

**Backend follows clean architecture:**
- **Models**: Database schema definitions
- **Repositories**: Data access layer (CRUD operations)
- **Services**: Business logic (orchestration)
- **Routes**: HTTP endpoints (request/response handling)
- **Utils**: Reusable helpers

**Frontend follows component-based architecture:**
- **Components**: Reusable UI pieces
- **Pages**: Route-level components
- **Services**: API communication
- **Hooks**: Reusable logic
- **Store**: Global state management

### Best Practices

- Type safety (TypeScript + Python type hints)
- Error handling at every layer
- Consistent API responses
- Modular, testable code
- Comments explaining decisions
- Environment-based configuration

## 🐛 Troubleshooting

### Database Connection Issues
- Verify Supabase URL and keys
- Check if IP is whitelisted in Supabase
- Ensure schema is created

### ChromaDB Connection Failed
- Check if Docker container is running: `docker ps`
- Verify port 8000 is not in use
- Restart container: `docker-compose restart`

### File Upload Fails
- Check Supabase Storage bucket exists
- Verify bucket permissions
- Ensure file is PDF format

### Authentication Errors
- Verify Clerk keys are correct
- Check token expiration
- Ensure CORS is configured

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

This is a complete, production-ready codebase. Feel free to:
- Fork and extend
- Report issues
- Suggest improvements
- Add features

## 🎓 Learning Resources

- **Flask**: https://flask.palletsprojects.com/
- **React**: https://react.dev/
- **Supabase**: https://supabase.com/docs
- **Clerk**: https://clerk.com/docs
- **ChromaDB**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/

---

**Built with ❤️ using only free-tier services**
