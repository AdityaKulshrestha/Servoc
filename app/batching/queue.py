import asyncio


# Later can be replaced with Redis, Kafka, RabbitMQ or own distributed queue
request_queue = asyncio.Queue()
