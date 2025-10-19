import asyncio
import json
import os
from dotenv import load_dotenv
from app.services.refine_prompts import refine_prompt, extarct_title
from app.services.youtube_service import fetch_top_videos
from app.services.openai import thumbnail_generation
from app.services.gemini_image_generation import thumbnail_generation2
from redis.asyncio import Redis
from app.db.supabase_client import supabase

load_dotenv()



QUEUE_NAME = "job_queue"
redis_conn = Redis(host="localhost", port=6379, db=0, decode_responses=True) 

print("[Worker] Connected to Valkey")

# --- Queue helpers ---

async def enqueue_job(job_data):
    await redis_conn.rpush(QUEUE_NAME, json.dumps(job_data))


async def dequeue_job():
    job_data = await redis_conn.lpop(QUEUE_NAME)
    if job_data:
        return json.loads(job_data)
    return None

# --- Job Handlers ---
async def process_refine_user_prompt(job):
    print(f"[Job] Refining prompt: {job}")
    user_query = job.get("user_query")
    job_id = job.get("job_id")


    if job_id:
        supabase.table("thumbnail_prompts").update({"status": "processing"}).eq("job_id", job_id).execute()

    refined_user_prompt = await refine_prompt(user_query)
    refined_title = await extarct_title(refined_user_prompt)

    if job_id:
        supabase.table("thumbnail_prompts").update({
            "refined_prompt": refined_user_prompt,
            "title": refined_title,
            "status": "completed"
        }).eq("job_id", job_id).execute()
        print("added")

    print(f"[YouTube Auto Search] {user_query} -> {refined_title}")

async def process_youtube_search(job):

    print(f"[Job] YouTube search: {job}")

    title = job.get("title")
    job_id = job.get("id")

    videos = await fetch_top_videos(title)

    if job_id:
        supabase.table("thumbnail_prompts").update({
            "youtube_examples": videos,
            "status": "completed"
        }).eq("job_id", job_id).execute()

    print(f"[YouTube Search] {title} -> {len(videos)} videos")

async def process_upload_prompt(job):
    print(f"[Job] Upload prompt: {job}")
    reference_images = job.get("reference_images", [])
    user_query = job.get("user_prompt")
    job_id = job.get("id")

    uploaded_urls = []

    for img in reference_images:
        file_bytes = await img.read()
        file_path = f"references/{img.filename}"
        res = supabase.storage.from_("thumbnails").upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": img.content_type}
        )
        if res.get("error"):
            print(f"[Upload Error] {img.filename}: {res['error']}")
            continue
        url = supabase.storage.from_("thumbnails").get_public_url(file_path)
        uploaded_urls.append(url)

    data = {
        "reference_images": uploaded_urls,
        "user_prompt": user_query,
        "status": "completed",
        "job_id": job_id
    }

    if job_id:
        supabase.table("thumbnail_prompts").update(data).eq("job_id", job_id).execute()
    else:
        supabase.table("thumbnail_prompts").insert(data).execute()

    print(f"[Upload Prompt] Saved record for job {job_id}")


async def process_generate_openai_template(job):
    
    print(f"[Job] Generate Template: {job}")

    job_id = job.get("job_id")

    if job_id:
        supabase.table("thumbnail_prompts").update({"status": "processing"}).eq("job_id", job_id).execute()

    # Fetch the record to get refined_prompt, reference_images, youtube_examples
    record_res = supabase.table("thumbnail_prompts").select("*").eq("job_id", job_id).execute()

    if not record_res.data or len(record_res.data) == 0:
        print(f"[Error] No record found for job_id {job_id}")
        return

    record = record_res.data[0]
    refined_prompt = record.get("refined_prompt", "")
    reference_images = record.get("reference_images", [])
    youtube_examples = record.get("youtube_examples", [])

    # Generate thumbnails using OpenAI
    try:
        generated_image_url = await thumbnail_generation(refined_prompt, reference_images, youtube_examples)
        if job_id:
            supabase.table("thumbnail_prompts").update({
                "generated_images": [generated_image_url],
                "status": "completed"
            }).eq("job_id", job_id).execute()
        print(f"[Template Generation] Generated image for job {job_id}")
    except Exception as e:
        print(f"[Template Generation Error] Job {job_id} failed: {e}")
        if job_id:
            supabase.table("thumbnail_prompts").update({"status": "failed"}).eq("job_id", job_id).execute()



async def process_generate_gemini_template(job):
    print(f"[Job] Generate Template: {job}")
    job_id = job.get("job_id")

    if job_id:
        supabase.table("thumbnail_prompts").update({"status": "processing"}).eq("job_id", job_id).execute()

    # Fetch the record to get refined_prompt, reference_images, youtube_examples
    record_res = supabase.table("thumbnail_prompts").select("*").eq("job_id", job_id).execute()
    if not record_res.data or len(record_res.data) == 0:
        print(f"[Error] No record found for job_id {job_id}")
        return

    record = record_res.data[0]
    refined_prompt = record.get("refined_prompt", "")
    reference_images = record.get("reference_images", [])
    youtube_examples = record.get("youtube_examples", [])

    # Generate thumbnails using Gemini
    try:
        generated_image_url = await thumbnail_generation2(refined_prompt, reference_images, youtube_examples)
        if job_id:
            supabase.table("thumbnail_prompts").update({
                "generated_images": [generated_image_url],
                "status": "completed"
            }).eq("job_id", job_id).execute()
        print(f"[Template Generation] Generated image for job {job_id}")

    except Exception as e:
        print(f"[Template Generation Error] Job {job_id} failed: {e}")
        if job_id:
            supabase.table("thumbnail_prompts").update({"status": "failed"}).eq("job_id", job_id).execute()


async def worker_loop():

    print("[Worker] Async worker started. Waiting for jobs...")

    while True:
        job = await dequeue_job()
        if job:
            print(f"[Worker] Got job: {job}")
            job_type = job.get("type")
            try:
                if job_type == "prompt_refinement":
                    await process_refine_user_prompt(job)
                elif job_type == "youtube_search":
                    await process_youtube_search(job)
                elif job_type == "upload_prompt":
                    await process_upload_prompt(job)
                elif job_type == "generate_openai_template":
                    await process_generate_openai_template(job)  
                elif job_type == "generate_gemini_template":
                    await process_generate_gemini_template(job)      
                else:
                    print(f"[Worker] Unknown job type: {job_type}")
            except Exception as e:
                print(f"[Worker Error] Job {job.get('id')} failed: {e}")
                if job.get("id"):
                    supabase.table("thumbnail_prompts").update({"status": "failed"}).eq("job_id", job.get("id")).execute()
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker_loop())
