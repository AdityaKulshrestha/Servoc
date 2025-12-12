from fastapi import FastAPI

from app.api.predict import router as predict_router
from app.batching.batcher import start_batch_worker


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_batch_worker()


app.include_router(predict_router)
