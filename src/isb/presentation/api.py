from fastapi import FastAPI

from isb.config import settings

# Initialize FastAPI application
app = FastAPI(
    title="Intelligent Second Brain (ISB.AI)",
    description="API Presentation layer for the ISB.AI Modular Monolith",
    version="0.1.0",
    debug=settings.DEBUG,
)


@app.get("/health", tags=["Lifecycle"])
def health_check() -> dict[str, str]:
    """Performs a simple readiness check of the FastAPI presentation node.

    Returns:
        dict[str, str]: Dict containing 'status': 'healthy' to indicate application readiness.
    """
    return {"status": "healthy"}
