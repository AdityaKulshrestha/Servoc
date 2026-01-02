import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import config
from app.api.predict import router as predict_router
from app.batching.queue import request_queue
from app.batching.batcher import DynamicBatcher
from app.engine.inference import InferenceEngine


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Global instances
engine: InferenceEngine = None
batcher: DynamicBatcher = None

@asynccontextmanager 
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    global engine, batcher

    logger.info("Starting up application")

    await request_queue.initialize()

    engine = InferenceEngine(config.engine)
    engine.initialize()

    batcher = DynamicBatcher(
        request_queue=request_queue,
        inference_fn=engine.infer,
        config=config.batcher
    )

    await batcher.start()

    logger.info("Server ready")

    yield


    # Cleanup
    logger.info("Shutting down...")
    await batcher.stop()
    engine.shutdown()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Servoc Inference Server",
    description="A high-performance inference server with dynamic batching",
    version="1.0.0",
    lifespan=lifespan
)

# Register routes 
app.include_router(predict_router, prefix="/v1", tags=["inference"])


@app.get("/")
async def root():
    return {"service": "Servoc Inference Server", "status": "running"}