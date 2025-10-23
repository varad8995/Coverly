from fastapi import FastAPI, WebSocket
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
# WebSocket for real-time updates
# --------------------------
CHANNEL = "thumbnail_updates"
clients = set()
redis_conn = Redis(host="valkey", port=6379, db=0, decode_responses=True)

@app.websocket("/ws/thumbnail")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await asyncio.sleep(1)  # keep connection alive
    except:
        pass
    finally:
        clients.remove(ws)

# --------------------------
# Redis subscriber to push updates
# --------------------------
async def redis_subscriber():
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(CHANNEL)

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
        if message and "data" in message:
            data = json.loads(message["data"])
            disconnected = []
            for ws in clients:
                try:
                    await ws.send_json(data)
                except:
                    disconnected.append(ws)
            for ws in disconnected:
                clients.remove(ws)
        await asyncio.sleep(0.01)  # prevent busy loop

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_subscriber())
