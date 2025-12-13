import asyncio
import time
import uuid
import logging
from typing import List

from fastapi import APIRouter, HTTPException
import torch

from app.api.models import PredictRequest, PredictResponse
from app.batching.queue import request_queue, InferenceRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/audio/transcription", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Submit an inference request
    """

    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())[:8]

    try:
        input_data = torch.tensor(request.input_vector, dtype=torch.float32)
        
        loop = asyncio.get_event_loop()
        future = loop.create_future()


        # Create request object
        inference_request = InferenceRequest(
            request_id=request_id,
            input_data=input_data,
            future=future,
            timestamp=time.perf_counter()
        )

        await request_queue.put(inference_request)
        logger.info(f"Request {request_id} enqueued")

        # Await the result
        result = await future

        latency_ms = (time.perf_counter() - start_time) * 1000

        return PredictResponse(
            request_id=request_id,
            prediction=result.tolist(),
            latency_ms=latency_ms
        )

    except Exception as e:
        logger.error(f"Error processing request {request_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "queue_size": request_queue.qsize()
    }