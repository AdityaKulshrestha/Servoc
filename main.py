import uvicorn
from app.config import config


def main():
    """Run the inference server."""
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        workers=config.workers,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()