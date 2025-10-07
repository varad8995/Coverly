from fastapi import APIRouter, Form, File, UploadFile
from typing import List, Optional
from dotenv import load_dotenv
from ..services.queue import enqueue_job
from db.supabase_client import supabase

import os
import uuid

load_dotenv()

router = APIRouter()


BUCKET_NAME = os.getenv("BUCKET_NAME")


# TODO: Refactor this to handle authentication and validation
@router.post("/upload-prompt")
async def upload_prompt_with_images(
    user_query: str = Form(None),
    reference_images: Optional[List[UploadFile]] = File(None),
):
    """
    Uploads images to private Supabase Storage, inserts job into table,
    and enqueues for AI processing.
    """
    job_id = str(uuid.uuid4())

    # Upload images to private bucket
    image_paths = []

    if reference_images:
        for img in reference_images:
            file_path = f"{job_id}/{img.filename}"
            res = supabase.storage.from_(BUCKET_NAME).upload(file_path, img.file.read())

            signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(file_path, 60*60*24*7)
            signed_url = signed["signedURL"]
            image_paths.append(signed_url)

    # Insert job into Supabase table 
    data = {"job_id": job_id}
    if user_query:
        data["user_query"] = user_query
    if image_paths:
        data["reference_images"] = image_paths  

    supabase.table("thumbnail_prompts").insert(data).execute()

    job_data = {
        "id": job_id,
        "type": "upload_prompt",
        "reference_images": image_paths,
        "user_prompt": user_query
    }
    await enqueue_job(job_data)

    return {"message": "Job enqueued", "job_id": job_id, "reference_images": image_paths, "user_prompt": user_query}
