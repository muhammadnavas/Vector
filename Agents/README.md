# Vector Backend API

Simple FastAPI-based REST API for the Vector project.

## Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   python main.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

Server runs at: `http://localhost:8000`

## API Endpoints

### Health
- `GET /health` - Health check

### Items (CRUD)
- `GET /api/items` - Get all items
- `GET /api/items/{id}` - Get specific item
- `POST /api/items` - Create new item
- `PUT /api/items/{id}` - Update item
- `DELETE /api/items/{id}` - Delete item

## Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
Agents/
├── main.py           # FastAPI app entry point
├── config.py         # Configuration settings
├── models.py         # Pydantic models/schemas
├── routes/
│   ├── health.py     # Health check endpoints
│   └── items.py      # Item CRUD endpoints
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## CORS

Frontend origins are whitelisted in `main.py`. Update the `allow_origins` list as needed.
