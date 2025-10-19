# ------------------------------
from redis.asyncio import Redis
import json


QUEUE_NAME = "job_queue"
redis_conn = Redis(host="valkey", port=6379, db=0, decode_responses=True)
print("[Worker] Connected to Redis (Valkey)")


async def enqueue_job(job_data):
    await redis_conn.rpush(QUEUE_NAME, json.dumps(job_data))

async def dequeue_job():
    job_data = await redis_conn.lpop(QUEUE_NAME)
    if job_data:
        return json.loads(job_data)
    return None