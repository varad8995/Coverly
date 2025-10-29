import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from dotenv import load_dotenv
from typing import TypedDict, List
from app.db.queue_connection import redis_conn, dequeue_job
from app.services.refine_prompts import refine_prompt, extract_title
from app.services.youtube_service import fetch_top_videos
from app.services.openai import thumbnail_generation
from app.services.gemini_image_generation import thumbnail_generation_gemini
from app.db.supabase_client import supabase
from app.utils.helper import upload_base64_to_s3, generate_presigned_url,compute_cache_key,publish_job_update
from langgraph.graph import StateGraph
from langsmith import traceable, Client
import logging
import builtins
import asyncio
import json

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


# ------------------------------
# Supabase helpers
# ------------------------------
async def db_update(table: str, data: dict, job_id: str):
    return await asyncio.to_thread(
        lambda: supabase.table(table).update(data).eq("job_id", job_id).execute()
    )


async def db_select(table: str, job_id: str):
    return await asyncio.to_thread(
        lambda: supabase.table(table).select("*").eq("job_id", job_id).execute()
    )


# ------------------------------
# LangGraph nodes
# ------------------------------
@traceable(name="Refine Prompt Node")
async def refine_prompt_node(state: ThumbnailState) -> dict:
    job_id = state["job_id"]
    try:
        await db_update("thumbnail_prompts", {"status": "refining_prompt"}, job_id)
        refined_prompt = await refine_prompt(state["user_query"],aspect_ratio=state.get("aspect_ratio", "16:9"),platform=state.get("platform", "YouTube"))
        title = await extract_title(refined_prompt,platform=state.get("platform", "YouTube"))
        await publish_job_update(job_id, "refining_prompt")

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
        await db_update("thumbnail_prompts", {"status": "fetching_youtube"}, job_id)
        videos = await fetch_top_videos(state["title"])
        await publish_job_update(job_id, "fetching_youtube")

        print("calling")
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
    await publish_job_update(job_id, "generating_openai")

    image_base64 = await thumbnail_generation(prompt, ref_images, [],aspect_ratio=state.get("aspect_ratio", "16:9"),platform=state.get("platform", "YouTube"))

    signed_url, s3_key = upload_base64_to_s3(image_base64, job_id)

    cache_key = await compute_cache_key(prompt, ref_images, "openai")
    await redis_conn.setex(
        f"img_cache:{cache_key}",
        7*24*3600,
        json.dumps({"s3_keys": [s3_key]})
    )
    await publish_job_update(job_id, "completed", [signed_url])

    await db_update("thumbnail_prompts", {
        "generated_images": [signed_url],
        "status": "completed"
    }, job_id)

    return {"generated_images": [signed_url], "status": "completed"}



@traceable(name="Generate Gemini Node")
async def generate_gemini_node(state: ThumbnailState) -> dict:
    job_id = state["job_id"]
    prompt = state["refined_prompt"]
    ref_images = state.get("reference_images", [])
    youtube_examples = state.get("youtube_examples", [])

    try:
        cache_key = await compute_cache_key(prompt, ref_images, "gemini")
        await publish_job_update(job_id, "generating_gemini")

        cached = await redis_conn.get(f"img_cache:{cache_key}")
        if cached:
            print(f"[Cache Hit] Job {job_id} (Gemini)")
            cached_data = json.loads(cached)
            s3_keys = cached_data["s3_keys"]
            presigned_urls = [
                generate_presigned_url(key) for key in s3_keys
            ]
            await publish_job_update(job_id, "completed", image_urls)

            await db_update("thumbnail_prompts", {
                "generated_imag_gemini": presigned_urls,
                "status": "completed"
            }, job_id)
            return {"generated_imag_gemini": presigned_urls, "status": "completed"}

        await db_update("thumbnail_prompts", {"status": "generating_gemini"}, job_id)
        result = await thumbnail_generation_gemini(prompt, ref_images, youtube_examples, job_id,aspect_ratio=state.get("aspect_ratio", "16:9"),platform=state.get("platform", "YouTube"))
        image_urls = result["image_urls"]
        await redis_conn.setex(
            f"img_cache:{cache_key}",
            7 * 24 * 3600,  
            json.dumps({"s3_keys": image_urls})
        )
        await publish_job_update(job_id, "completed", image_urls)

        await db_update("thumbnail_prompts", {
            "generated_imag_gemini": image_urls,
            "status": "completed"
        }, job_id)
        return {"generated_imag_gemini": image_urls, "status": "completed"}

    except Exception as e:
        await db_update("thumbnail_prompts", {"status": "failed"}, job_id)
        print(f"[Gemini Node Error] Job {job_id} failed: {e}")
        return {"status": "failed"}

# ------------------------------
# Build LangGraph
# ------------------------------

graph = StateGraph(state_schema=ThumbnailState)

graph.add_node("refine_prompt", refine_prompt_node)
graph.add_node("fetch_youtube", fetch_youtube_node)
graph.add_node("generate_openai", generate_openai_node)
graph.add_node("generate_gemini", generate_gemini_node)

def decide_next(state):
    if state.get("platform") == "YouTube":
        return "fetch_youtube"
    else:
        return "generate_openai"

graph.add_conditional_edges(
    "refine_prompt",
    decide_next,
    {
        "fetch_youtube": "fetch_youtube",
        "generate_openai": "generate_openai",
    }
)

graph.add_edge("fetch_youtube", "generate_openai")
graph.add_edge("fetch_youtube", "generate_gemini")
graph.set_entry_point("refine_prompt")
graph.compile()


# ------------------------------
# Worker loop
# ------------------------------
async def worker_loop():
    print("[Worker] Started. Waiting for jobs...")
    while True:
        job = await dequeue_job()
        if not job:
            await asyncio.sleep(1)
            continue

        job_id = job.get("id")
        user_id = job.get("user_id") 
        if not user_id:
            print(f"[Worker Error] Job {job_id} has no user_id")
            continue

        print(f"[Worker] Got job: {job_id} for user {user_id}")

        try:
            record_res = await db_select("thumbnail_prompts", job_id)
            if not record_res.data or len(record_res.data) == 0:
                print(f"[Worker Error] No record found for job {job_id}")
                continue

            record = record_res.data[0]

            # Ensure job belongs to the same user
            if record.get("user_id") != user_id:
                print(f"[Worker Error] User mismatch for job {job_id}")
                continue

            state = {
                "job_id": record["job_id"],
                "user_id": user_id,  
                "user_query": record.get("user_query", ""),
                "reference_images": record.get("reference_images", []),
                "youtube_examples": record.get("youtube_examples", []),
                "platform": record.get("platform", "YouTube"),
                "aspect_ratio": record.get("aspect_ratio", "16:9"),
            }

            state.update(await refine_prompt_node(state))

            if state.get("platform") == "YouTube":
                state.update(await fetch_youtube_node(state))

            openai_result, gemini_result = await asyncio.gather(
                generate_openai_node(state),
                generate_gemini_node(state)
            )

            state["generated_images"] = (
                openai_result.get("generated_images", []) +
                gemini_result.get("generated_images", [])
            )

            await db_update("thumbnail_prompts", {
                "generated_images": state["generated_images"],
                "status": "completed"
            }, job_id)

        except Exception as e:
            print(f"[Worker Error] Job {job_id} failed: {e}")
            await db_update("thumbnail_prompts", {"status": "failed"}, job_id)





if __name__ == "__main__":
    asyncio.run(worker_loop())
