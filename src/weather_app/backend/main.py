import uvicorn

def run_app(host="0.0.0.0", port=8001):
    """Run the FastAPI application using Uvicorn server."""
    uvicorn.run(
        "weather_app.backend.api.app:app",
        host=host,
        port=port,
        reload=True
    )

if __name__ == "__main__":
    run_app()