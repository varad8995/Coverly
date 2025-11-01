from redis.asyncio import Redis
import json
import os
from dotenv import load_dotenv

load_dotenv()
QUEUE_NAME = "job_queue"

# Use Upstash Redis instead of local Valkey
REDIS_URL = os.getenv(
    "REDIS_URL",
)

redis_conn = Redis.from_url(REDIS_URL, decode_responses=True)
print("[Worker] Connected to Upstash Redis ✅")


async def enqueue_job(job_data):
    """Push a new job to the queue"""
    await redis_conn.rpush(QUEUE_NAME, json.dumps(job_data))
    print(f"[Worker] Job enqueued: {job_data['job_id']}")


async def dequeue_job():
    """Pop a job from the queue"""
    job_data = await redis_conn.lpop(QUEUE_NAME)
    if job_data:
        data = json.loads(job_data)
        print(f"[Worker] Dequeued job: {data['job_id']}")
        return data
    return None
