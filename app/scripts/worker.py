import os
import sys
import json
import asyncio
import logging
import builtins
from typing import TypedDict, List


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
if root_dir not in sys.path:
    sys.path.append(root_dir)
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langsmith import traceable, Client

from app.db.queue_connection import redis_conn, dequeue_job
from app.services.refine_prompts import refine_prompt, extract_title
from app.services.youtube_service import fetch_top_videos
from app.services.openai import thumbnail_generation
from app.services.gemini_image_generation import thumbnail_generation_gemini
from app.db.supabase_client import supabase
from app.utils.helper import (
    upload_base64_to_s3,
    generate_presigned_url,
    compute_cache_key,
    publish_job_update,
)

# ------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("coverly.worker")

_original_print = builtins.print
def _print(*args, sep=" ", end="\n", file=None, flush=False, level="info"):
    try:
        message = sep.join(str(a) for a in args)
        if message.endswith("\n"):
            message = message[:-1]
        if hasattr(logger, level):
            getattr(logger, level)(message)
        else:
            logger.info(message)
    except Exception:
        _original_print(*args, sep=sep, end=end, file=file, flush=flush)
builtins.print = _print

load_dotenv()
client = Client()

# ------------------------------------------------------------------
# State Schema
# ------------------------------------------------------------------
class ThumbnailState(TypedDict, total=False):
    user_query: str
    job_id: str
    refined_prompt: str
    title: str
    reference_images: List[str]
    youtube_examples: List[dict]
    generated_images: List[str]
    aspect_ratio: str
    platform: str
    status: str
    generator_provider: str

# ------------------------------------------------------------------
# Supabase Helpers
# ------------------------------------------------------------------
async def db_update(table: str, data: dict, job_id: str):
    return await asyncio.to_thread(
        lambda: supabase.table(table).update(data).eq("job_id", job_id).execute()
    )

async def db_select(table: str, job_id: str):
    return await asyncio.to_thread(
        lambda: supabase.table(table).select("*").eq("job_id", job_id).execute()
    )

# ------------------------------------------------------------------
# LangGraph Nodes
# ------------------------------------------------------------------
@traceable(name="Refine Prompt Node")
async def refine_prompt_node(state: ThumbnailState) -> dict:
    job_id = state["job_id"]
    try:
        await publish_job_update(job_id, "refining_prompt", progress=10, message="Refining the input prompt...")
        await db_update("thumbnail_prompts", {"status": "refining_prompt"}, job_id)

        refined_prompt = await refine_prompt(
            state["user_query"],
            aspect_ratio=state.get("aspect_ratio", "16:9"),
            platform=state.get("platform", "YouTube")
        )
        title = await extract_title(refined_prompt, platform=state.get("platform", "YouTube"))

        await db_update("thumbnail_prompts", {
            "refined_prompt": refined_prompt,
            "title": title,
            "status": "refined"
        }, job_id)

        return {"refined_prompt": refined_prompt, "title": title, "status": "refined"}

    except Exception as e:
        await db_update("thumbnail_prompts", {"status": "failed"}, job_id)
        print(f"[Error] refine_prompt_node: {e}")
        return {"status": "failed"}

@traceable(name="Fetch YouTube Node")
async def fetch_youtube_node(state: ThumbnailState) -> dict:
    job_id = state["job_id"]
    try:
        await publish_job_update(job_id, "fetching_youtube", progress=30, message="Fetching YouTube references...")
        await db_update("thumbnail_prompts", {"status": "fetching_youtube"}, job_id)

        videos = await fetch_top_videos(state["title"])
        await db_update("thumbnail_prompts", {
            "youtube_examples": videos,
            "status": "videos_fetched"
        }, job_id)

        return {"youtube_examples": videos, "status": "videos_fetched"}
    except Exception as e:
        await db_update("thumbnail_prompts", {"status": "failed"}, job_id)
        print(f"[Error] fetch_youtube_node: {e}")
        return {"status": "failed"}

@traceable(name="Generate OpenAI Node")
async def generate_openai_node(state: ThumbnailState) -> dict:
    job_id = state["job_id"]
    prompt = state["refined_prompt"]
    ref_images = state.get("reference_images", [])
    try:
        await publish_job_update(job_id, "generating_openai", progress=60, message="Generating thumbnail with OpenAI...")
        image_base64 = await thumbnail_generation(prompt, ref_images, [], aspect_ratio=state.get("aspect_ratio", "16:9"))

        signed_url, s3_key = upload_base64_to_s3(image_base64, job_id)
        cache_key = await compute_cache_key(prompt, ref_images, "openai")

        await redis_conn.setex(f"img_cache:{cache_key}", 7*24*3600, json.dumps({"s3_keys": [s3_key]}))
        await publish_job_update(job_id, "completed", progress=100, message="Thumbnail generated via OpenAI", generated_images=[signed_url])

        await db_update("thumbnail_prompts", {"generated_images": [signed_url], "status": "completed"}, job_id)
        return {"generated_images": [signed_url], "status": "completed"}

    except Exception as e:
        await db_update("thumbnail_prompts", {"status": "failed"}, job_id)
        print(f"[Error] generate_openai_node: {e}")
        return {"status": "failed"}

@traceable(name="Generate Gemini Node")
async def generate_gemini_node(state: ThumbnailState) -> dict:
    job_id = state["job_id"]
    prompt = state["refined_prompt"]
    ref_images = state.get("reference_images", [])
    youtube_examples = state.get("youtube_examples", [])
    try:
        await publish_job_update(job_id, "generating_gemini", progress=60, message="Generating thumbnail with Gemini...")
        cache_key = await compute_cache_key(prompt, ref_images, "gemini")

        cached = await redis_conn.get(f"img_cache:{cache_key}")
        if cached:
            cached_data = json.loads(cached)
            s3_keys = cached_data["s3_keys"]
            presigned_urls = [generate_presigned_url(k) for k in s3_keys]
            await publish_job_update(job_id, "completed", progress=100, generated_images=presigned_urls)
            await db_update("thumbnail_prompts", {"generated_images_gemini": presigned_urls, "status": "completed"}, job_id)
            return {"generated_images_gemini": presigned_urls, "status": "completed"}

        result = await thumbnail_generation_gemini(prompt, ref_images, youtube_examples, job_id, aspect_ratio=state.get("aspect_ratio", "16:9"))
        image_urls = result["image_urls"]

        await redis_conn.setex(f"img_cache:{cache_key}", 7 * 24 * 3600, json.dumps({"s3_keys": image_urls}))
        await publish_job_update(job_id, "completed", progress=100, generated_images=image_urls)
        await db_update("thumbnail_prompts", {"generated_images_gemini": image_urls, "status": "completed"}, job_id)

        return {"generated_images_gemini": image_urls, "status": "completed"}

    except Exception as e:
        await db_update("thumbnail_prompts", {"status": "failed"}, job_id)
        print(f"[Gemini Node Error] Job {job_id} failed: {e}")
        return {"status": "failed"}

# ------------------------------------------------------------------
# LangGraph Definition
# ------------------------------------------------------------------
graph = StateGraph(state_schema=ThumbnailState)
graph.add_node("refine_prompt", refine_prompt_node)
graph.add_node("fetch_youtube", fetch_youtube_node)
graph.add_node("generate_openai", generate_openai_node)
graph.add_node("generate_gemini", generate_gemini_node)

def decide_next(state):
    return "fetch_youtube" if state.get("platform") == "YouTube" else "generate_openai"

graph.add_conditional_edges("refine_prompt", decide_next, {"fetch_youtube": "fetch_youtube", "generate_openai": "generate_openai"})
graph.add_edge("fetch_youtube", "generate_openai")
graph.add_edge("fetch_youtube", "generate_gemini")
graph.set_entry_point("refine_prompt")
graph.compile()

# ------------------------------------------------------------------
# Worker Loop
# ------------------------------------------------------------------
async def worker_loop():
    print("[Worker] Started. Waiting for jobs...")
    try:
        await redis_conn.ping()
        print("[Worker] Connected to Redis ✅")
    except Exception as e:
        print(f"[Worker] Redis connection failed: {e}")

    while True:
        job = await dequeue_job()
        if not job:
            await asyncio.sleep(1)
            continue

        job_id = job.get("job_id")
        user_id = job.get("user_id")
        print(f"[Worker] Got job: {job_id} for user {user_id}")

        try:
            record_res = await db_select("thumbnail_prompts", job_id)
            if not record_res.data:
                print(f"[Worker Error] No record found for job {job_id}")
                continue

            record = record_res.data[0]
            state = {
                "job_id": job_id,
                "user_id": user_id,
                "user_query": record.get("user_query", ""),
                "reference_images": record.get("reference_images", []),
                "youtube_examples": record.get("youtube_examples", []),
                "platform": record.get("platform", "YouTube"),
                "aspect_ratio": record.get("aspect_ratio", "16:9"),
                "generator_provider": record.get("generator_provider", "gemini"),
            }

            # --- Execute pipeline ---
            state.update(await refine_prompt_node(state))
            if state.get("platform") == "YouTube":
                state.update(await fetch_youtube_node(state))

            provider = record.get("generator_provider", "gemini").lower()
            if provider == "openai":
                await generate_openai_node(state)
            elif provider == "gemini":
                await generate_gemini_node(state)
            elif provider == "both":
                await asyncio.gather(generate_openai_node(state), generate_gemini_node(state))

        except Exception as e:
            print(f"[Worker Error] Job {job_id} failed: {e}")
            await db_update("thumbnail_prompts", {"status": "failed"}, job_id)

if __name__ == "__main__":
    asyncio.run(worker_loop())
