from fastapi import FastAPI
import asyncio
import uvicorn


app = FastAPI()


# Queue
request_queue = asyncio.Queue()

@