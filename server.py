from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.routes import upload
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from redis.asyncio import Redis
import os
import logging

# --------------------------
# FastAPI Setup
# --------------------------
app = FastAPI(
    title="Coverly API",
    description="Backend API for generating AI thumbnails with YouTube reference search.",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "up and running 🚀"}

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])

# --------------------------
# Redis (Upstash) Setup
# --------------------------
REDIS_URL = os.getenv("REDIS_URL")
redis_conn = Redis.from_url(REDIS_URL, decode_responses=True)
CHANNEL = "thumbnail_updates"

# --------------------------
# Logging setup
# --------------------------
logger = logging.getLogger("coverly.websocket")
logger.setLevel(logging.INFO)

# Each job_id has a set of connected WebSocket clients
clients_by_job: dict[str, set[WebSocket]] = {}

# --------------------------
# WebSocket Endpoint
# --------------------------
@app.websocket("/ws/thumbnail/{job_id}")
async def websocket_endpoint(ws: WebSocket, job_id: str):
    """Each WebSocket listens for updates for a specific job_id."""
    await ws.accept()
    logger.info(f"🔌 WebSocket connected for job_id={job_id}")

    clients_by_job.setdefault(job_id, set()).add(ws)

    try:
        while True:
            # Keep alive or listen for ping/pong
            await asyncio.sleep(20)
    except WebSocketDisconnect:
        logger.info(f"❌ WebSocket disconnected for job_id={job_id}")
    finally:
        clients_by_job[job_id].discard(ws)
        if not clients_by_job[job_id]:
            clients_by_job.pop(job_id, None)

# --------------------------
# Redis Subscriber
# --------------------------
async def redis_subscriber():
    """Listen for published thumbnail updates and forward them to WebSocket clients."""
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(CHANNEL)
    logger.info(f"🧠 Subscribed to Redis channel: {CHANNEL}")

    while True:
        try:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message and "data" in message:
                try:
                    data = json.loads(message["data"])
                    job_id = data.get("job_id")
                    if not job_id:
                        continue  # skip malformed payloads

                    if job_id in clients_by_job:
                        # broadcast to all connected clients for this job_id
                        disconnected = []
                        for ws in list(clients_by_job[job_id]):
                            try:
                                await ws.send_json(data)
                            except Exception:
                                disconnected.append(ws)

                        for ws in disconnected:
                            clients_by_job[job_id].discard(ws)
                        if not clients_by_job[job_id]:
                            clients_by_job.pop(job_id, None)
                except json.JSONDecodeError:
                    logger.warning("⚠️ Received invalid JSON from Redis.")
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_subscriber())
    logger.info("🚀 WebSocket + Redis subscriber started.")
