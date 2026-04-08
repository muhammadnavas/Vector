# Vector

AI-powered automated API testing platform with LangGraph multi-agent orchestration.

## Overview

Vector is a full-stack application that combines a FastAPI backend with a modern React frontend to provide intelligent, autonomous API testing capabilities. It uses LangGraph for multi-agent orchestration, leveraging state-of-the-art language models to generate, execute, and analyze API tests automatically.

## Features

- 🤖 **Multi-Agent Architecture**: LangGraph-powered agent orchestration for intelligent test generation
- 🧪 **Automated API Testing**: Generate and execute comprehensive API tests with minimal configuration
- 💾 **Execution History**: Track and analyze test results over time
- 📊 **Test Visualization**: Beautiful UI with real-time execution feedback
- 🔌 **GitHub Integration**: Webhook support for CI/CD pipeline integration
- 🌐 **Multi-LLM Support**: Compatible with OpenAI and Google GenAI models
- ♿ **RESTful API**: Complete REST API for programmatic access
- 🎨 **Modern UI**: React-based interface with Tailwind CSS styling

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Agent Orchestration**: LangGraph 0.1.0, LangChain 0.1.0
- **AI Models**: LangChain-OpenAI, LangChain-Google-GenAI
- **Data Validation**: Pydantic 2.5.0
- **GitHub Integration**: PyGithub 2.1.1

### Frontend
- **Framework**: React 19.2.0
- **Build Tool**: Vite 7.3.1
- **Styling**: Tailwind CSS 3.4.19
- **Visualization**: Three.js 0.183.2
- **Linting**: ESLint 9.39.1

## Project Structure

```
Vector/
├── Agents/                 # Backend Python application
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # Pydantic data models
│   ├── nodes.py           # LLM node definitions
│   ├── graph.py           # LangGraph workflow definition
│   ├── graph_state.py     # State management for graph
│   ├── config.py          # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── routes/            # API route handlers
│       ├── health.py      # Health check endpoint
│       ├── items.py       # Item CRUD operations
│       └── pipeline.py    # Pipeline and webhook handling
│
└── frontend/              # React application
    ├── src/
    │   ├── App.jsx        # Main app component
    │   ├── main.jsx       # Entry point
    │   ├── services/
    │   │   └── api.js     # API client
    │   └── style/         # Component styles and JSX
    │       ├── HomePage.jsx
    │       ├── TestRunner.jsx
    │       ├── ExecutionHistory.jsx
    │       ├── Header.jsx
    │       └── FloatingLines.jsx
    ├── index.html         # HTML template
    ├── vite.config.js     # Vite configuration
    ├── tailwind.config.js # Tailwind configuration
    └── package.json       # Node dependencies
```

## Prerequisites

- **Python** 3.8+
- **Node.js** 18+
- **npm** or **yarn**
- API keys for AI models:
  - OpenAI API key (if using OpenAI)
  - Google GenAI API key (if using Google)

## Installation

### Backend Setup

1. Navigate to the Agents directory:
```bash
cd Agents
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the Agents directory:
```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
GITHUB_TOKEN=your_github_token
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Development Environment

#### Start Backend

From the `Agents` directory:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

#### Start Frontend

From the `frontend` directory:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Production Build

#### Backend
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
npm run build
npm run preview
```

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Alternative**: http://localhost:8000/redoc

### Key Endpoints

- **GET** `/` - API status and available endpoints
- **GET** `/health` - Health check
- **POST** `/api/items` - Create a new item
- **GET** `/api/items` - List all items
- **POST** `/pipeline/test-run` - Execute a manual test run
- **POST** `/pipeline/webhook/github` - GitHub webhook for CI/CD integration

## Configuration

### Environment Variables

Create a `.env` file in the `Agents` directory:

```env
# AI Provider Configuration
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# GitHub Integration
GITHUB_TOKEN=your_token_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### API CORS Settings

The backend is configured to accept requests from:
- http://localhost:5173 (Vite dev server)
- http://localhost:3000 (Alternative frontend port)

Modify the `main.py` CORS configuration to add additional allowed origins.

## Development

### Code Quality

#### Frontend Linting
```bash
cd frontend
npm run lint
```

### Project Notes

- The graph state and LangGraph nodes are configured in `graph_state.py` and `nodes.py`
- API models and validation schemas are defined in `models.py`
- Route handlers follow FastAPI best practices with proper dependency injection

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Ensure code quality:
   - Backend: Follow PEP 8 conventions
   - Frontend: Run `npm run lint`
4. Submit a pull request

## License

This project is provided as-is for development and testing purposes.

## Support

For issues, questions, or contributions, please open an issue in the repository.
