from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.routes import upload
import asyncio
import json
from redis.asyncio import Redis

app = FastAPI(
    title="Coverly API",
    description="Backend API for generating AI thumbnails with YouTube reference search.",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "up and running 🚀"}

app.include_router(upload.router, prefix="/api", tags=["Upload"])

# --------------------------
# Redis + WebSocket Setup
# --------------------------
CHANNEL = "thumbnail_updates"
redis_conn = Redis(host="valkey", port=6379, db=0, decode_responses=True)

clients_by_job: dict[str, set[WebSocket]] = {}

@app.websocket("/ws/thumbnail/{job_id}")
async def websocket_endpoint(ws: WebSocket, job_id: str):
    """Each WebSocket listens for updates for a specific job_id."""
    await ws.accept()

    if job_id not in clients_by_job:
        clients_by_job[job_id] = set()
    clients_by_job[job_id].add(ws)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup on disconnect
        clients_by_job[job_id].remove(ws)
        if not clients_by_job[job_id]:
            del clients_by_job[job_id]

# --------------------------
# Redis subscriber to push updates
# --------------------------
async def redis_subscriber():
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(CHANNEL)

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
        if message and "data" in message:
            try:
                data = json.loads(message["data"])
                job_id = data.get("job_id")
                if not job_id:
                    continue  # ignore messages without job_id

                # Send updates only to clients tracking this job_id
                if job_id in clients_by_job:
                    disconnected = []
                    for ws in clients_by_job[job_id]:
                        try:
                            await ws.send_json(data)
                        except Exception:
                            disconnected.append(ws)
                    for ws in disconnected:
                        clients_by_job[job_id].remove(ws)
                    # clean up empty sets
                    if not clients_by_job[job_id]:
                        del clients_by_job[job_id]
            except json.JSONDecodeError:
                pass
        await asyncio.sleep(0.01)  # prevent busy loop

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_subscriber())
