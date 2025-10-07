import json
import asyncio
from redis.asyncio import Redis

QUEUE_NAME = "job_queue"

# Connect to Valkey using Docker service name
def get_async_valkey_connection():
    return Redis(host="valkey", port=6379, db=0, decode_responses=True)

# Enqueue a job (async)
async def enqueue_job(job_data):
    conn = get_async_valkey_connection()
    await conn.rpush(QUEUE_NAME, json.dumps(job_data))
    print(f"[Queue] Enqueued job: {job_data.get('id')}")

# Dequeue a job (async)
async def dequeue_job():
    conn = get_async_valkey_connection()
    job = await conn.lpop(QUEUE_NAME)
    if job:
        job_obj = json.loads(job)
        print(f"[Queue] Dequeued job: {job_obj.get('id')}")
        return job_obj
    return None
