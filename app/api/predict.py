import asyncio
import time
import uuid
import logging
from typing import List, Optional

from fastapi import (
    APIRouter, HTTPException, 
    UploadFile, Form, File
)
import torch

from app.utils.audio import decode_audio
from app.api.models import TranscriptionResponse
from app.batching.queue import request_queue, InferenceRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/audio/transcriptions", response_model=TranscriptionResponse)
async def transcribe(
        file: UploadFile = File(...),
        model: str = Form(..., description="ID of the model to use (e.g., whisper-1)"),
        language: Optional[str] = Form(None, description="ISO-639-1 language code (e.g. 'en')"),
        prompt: Optional[str] = Form(None, description="Optional text to guide style or continue audio"),
        response_format: Optional[str] = Form("json", description="json, text, srt, verbose_json, or vtt"),
        temperature: Optional[float] = Form(0.0, description="Sampling temperature, between 0 and 1"),
        timestamp_granularities: Optional[List[str]] = Form(None, description="['word'] or ['segment']")
    ):
    """
    Submit an inference request
    """

    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())[:8]

    try:        
        file_bytes = await file.read()

        # Decoding audio to numpy
        audio_sample = await decode_audio(file_bytes, target_sample_rate=16000)
        
        loop = asyncio.get_event_loop()
        future = loop.create_future()


        # Create request object
        inference_request = InferenceRequest(
            request_id=request_id,
            audio=audio_sample.audio,
            sample_rate=audio_sample.sample_rate,
            duration=audio_sample.duration,
            future=future,
            timestamp=time.perf_counter(),
        )

        await request_queue.put(inference_request)
        logger.info(f"Request {request_id} enqueued")

        # Await the result
        transcription = await future

        latency_ms = (time.perf_counter() - start_time) * 1000

        return TranscriptionResponse(
            text=transcription,
            usage={
                "audio_seconds": audio_sample.duration,
                "latency_ms": latency_ms
            }
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