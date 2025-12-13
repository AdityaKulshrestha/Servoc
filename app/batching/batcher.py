import asyncio
import time 
import logging 
from typing import List
import torch


from app.batching.queue import RequestQueue, InferenceRequest
from app.config import BatcherConfig


logger = logging.getLogger(__name__)


class DynamicBatcher:
    """
    Collects individual requests and batches them together 
    Triggers batch processing when:
    - max batch size is reached 
    - max wait time is exceeded
    """

    def __init__(
        self,
        request_queue: RequestQueue,
        inference_fn,
        config: BatcherConfig,
    ):
        self.request_queue = request_queue
        self.inference_fn = inference_fn
        self.config = config 

        self._running = False
        self._task: asyncio.Task = None

    async def start(self):
        """Start the batcher loop"""

        if self._running:
            logger.warning("Batcher is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._batch_loop())
        logger.info("Batcher started")

    async def stop(self):
        self._running = False
        if self._task: 
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Batcher stopped")

    async def _batch_loop(self):
        """Main loop for fetching and processing batches"""
        while self._running:
            try:
                batch = await self._collect_batch()
                if batch:
                    await self._process_batch(batch)
            except asyncio.CanclledError:
                break
            except Exception as e:
                logger.error(f"Error in batch loop: {e}")
                await asyncio.sleep(0.1)

    async def _collect_batch(self) -> List[InferenceRequest]:
        """Collect requests into a batch until full or max timeout"""
        batch: List[InferenceRequest] = []
        batch_start_time = None

        while len(batch) < self.config.max_batch_size:
            if batch_start_time is None:
                timeout = None
            else:
                elapsed_ms = (time.perf_counter() - batch_start_time) * 1000
                remaining_ms = self.config.max_wait_time_ms - elapsed_ms 
                if remaining_ms <= 0:
                    break
                timeout = remaining_ms / 1000

            try:
                request = await asyncio.wait_for(
                    self.request_queue.get(), timeout=timeout
                )
                batch.append(request)

                if batch_start_time is None:
                    batch_start_time = time.perf_counter()

            except asyncio.TimeoutError:
                break

        return batch
    

    async def _process_batch(self, batch: List[InferenceRequest]):
        """Process a batch of requests."""
        if not batch:
            return
        

        logger.debug(f"Processing batch of size {len(batch)}")

        try:
            # Stack inputs into a single tensor
            inputs = torch.stack([req.input_data for req in batch])

            # Run inference (in thread pool to not block event loop)
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self.inference_fn,
                inputs
            )


            # Distribute results back to individual requests
            for i, request in enumerate(batch):
                try:
                    request.future.set_result(results[i])
                except Exception as e:
                    request.future.set_exception(e)

        except Exception as e:
            logger.error(f"Batch processing error: {e}", exc_info=True)
            
            # Set exception for all request in batch
            for request in batch:
                if not request.future.done():
                    request.future.set_exception(e)
