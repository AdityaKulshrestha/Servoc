import asyncio 
from dataclasses import dataclass 
from typing import Any, Optional
import torch
import numpy as np


@dataclass
class InferenceRequest:
    """Data class representing an inference request."""
    request_id: str
    audio: np.ndarray
    sample_rate: int
    duration: float
    future: asyncio.Future
    timestamp: float
    metadata: Optional[dict] = None


class RequestQueue:
    """Async queue for managing inference requests."""

    def __init__(self, max_size: int = 1000):
        self._queue: asyncio.Queue = None
        self._maxsize = max_size

    async def initialize(self):
        """Initialize the async queue"""
        if self._queue is None:
            self._queue = asyncio.Queue(maxsize=self._maxsize)

    async def put(self, request: InferenceRequest):
        """Put an inference request into the queue"""
        if self._queue is None:
            await self.initialize()
        await self._queue.put(request)

    async def get(self) -> InferenceRequest:
        """Get a request from the queue"""
        if self._queue is None:
            await self.initialize()
        return await self._queue.get()
    
    def qsize(self) -> int:
        """Return current queue size"""
        if self._queue is None:
            return 0
        return self._queue.qsize()
    
    def empty(self) -> bool:
        """Check if the queue is empty"""
        if self._queue is None:
            return True
        return self._queue.empty()
        

request_queue = RequestQueue(max_size=1024)