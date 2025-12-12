from fastapi import APIRouter
from app.batching.queue import request_queue
import asyncio
import torch


router = APIRouter()

@router.post("/predict")
async def predict(input_vector: list[float]):
    input_data = torch.tensor(input_vector, dtype=torch.float32)

    loop = asyncio.get_event_loop()
    future = loop.create_future()

    await request_queue.put((input_data, future))
    result = await future

    return {"prediction": result.tolist()}
