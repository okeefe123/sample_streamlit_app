import uvicorn
from backend.api.app import app

if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn server
    uvicorn.run(
        "backend.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )