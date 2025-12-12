import asyncio
import torch

from app.batching.queue import request_queue
from app.engine.inference import model_inference
from app.config import BATCH_SIZE, BATCH_TIMEOUT

def start_batch_worker():
    asyncio.create_task(batch_worker())


async def batch_worker():
    while True:
        inputs = []
        futures = []

        input_data, future = await request_queue.get()
        inputs.append(input_data)
        futures.append(future)

        start_time = asyncio.get_event_loop().time()

        while len(inputs) < BATCH_SIZE:
            try:
                timeout = BATCH_TIMEOUT - (asyncio.get_event_loop().time() - start_time)
                if timeout <= 0:
                    break

                input_data, future = await asyncio.wait_for(request_queue.get(), timeout=timeout)
                inputs.append(input_data)
                futures.append(future)
            
            except asyncio.TimeoutError:
                break

        
        # Padding
        max_len = max(data.shape[0] for data in inputs)
        padded_inputs = [torch.nn.functional.pad(data, (0, max_len - data.shape[0])) for data in inputs]
        batch = torch.stack(padded_inputs)


        output = model_inference(batch)

        for i, future in enumerate(futures):
            future.set_result(output[i])