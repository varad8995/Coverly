from fastapi import APIRouter, Form, File, UploadFile, HTTPException, status, Depends
from typing import List, Optional
from ..db.queue_connection import enqueue_job
from ..db.s3_storage import upload_to_s3
from ..db.supabase_client import supabase
from ..models.upload_prompt import UploadPromptRequest
from ..dependencies.auth import verify_supabase_token
import uuid
import logging
import asyncio

logger = logging.getLogger("coverly.api")
router = APIRouter()


# ----------------------
def initialize_user_credits(user_id: str):
    """Ensure the user has a credits record; initialize with 5 if missing."""
    res = supabase.table("user_credits").select("*").eq("user_id", user_id).execute()
    if not res.data:
        supabase.table("user_credits").insert({"user_id": user_id, "credits": 5}).execute()


def get_user_credits(user_id: str) -> int:
    res = supabase.table("user_credits").select("credits").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]["credits"]
    return 0


def consume_credit(user_id: str):
    """Atomically decrement 1 credit."""
    res = supabase.table("user_credits").select("credits").eq("user_id", user_id).execute()
    if res.data and len(res.data) > 0:
        current_credits = res.data[0]["credits"]
        supabase.table("user_credits").update({
            "credits": max(current_credits - 1, 0)
        }).eq("user_id", user_id).execute()


# ----------------------
# Upload Prompt Endpoint
# ----------------------
@router.post(
    "/upload-prompt",
    response_model=UploadPromptRequest,
    status_code=status.HTTP_201_CREATED,
    summary="Upload prompt and reference images",
    description="Uploads reference images to S3, saves metadata to Supabase, enqueues the thumbnail generation job, and manages credits."
)
async def upload_prompt_with_images(
    user_query: Optional[str] = Form(None),
    aspect_ratio: Optional[str] = Form("16:9"),
    platform: Optional[str] = Form("YouTube"),
    generator_provider: Optional[str] = Form("openai"),
    reference_images: Optional[UploadFile] = File(None),

    user=Depends(verify_supabase_token)  
):
    user_id = user['id']
    provider = user.get("app_metadata", {}).get("provider", "unknown")

    initialize_user_credits(user_id)
    remaining_credits = get_user_credits(user_id)

    if remaining_credits <= 0:
        raise HTTPException(
            status_code=403,
            detail="You have exhausted your free credits."
        )

    consume_credit(user_id)
    remaining_credits -= 1

    job_id = str(uuid.uuid4())
    image_urls: List[str] = []

    try:
        if reference_images:
                # Create a single task list containing the single file operation
                upload_tasks = [
                    upload_to_s3(
                        job_id, 
                        reference_images.file, 
                        reference_images.filename, 
                        reference_images.content_type or "image/jpeg"
                    )
                ]
                
                results = await asyncio.gather(*upload_tasks, return_exceptions=True)
                
                if results and not isinstance(results[0], Exception):
                    image_urls.append(results[0])
                elif results and isinstance(results[0], Exception):
                    logger.error(f"[Upload Error] {reference_images.filename}: {results[0]}")

        if not user_query and not image_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must provide either a text prompt or at least one reference image."
            )

        record = {
            "job_id": job_id,
            "user_id": user_id,           
            "provider": provider,
            "user_query": user_query,
            "reference_images": image_urls or [],
            "aspect_ratio": aspect_ratio,    
            "platform": platform,   
            "generator_provider": generator_provider,
            "status": "queued",
            "credits_consumed": 1
        }

        response = supabase.table("thumbnail_prompts").insert(record).execute()
        if not response.data:
            logger.error(f"[Supabase Error] Failed to insert job {job_id}")
            raise HTTPException(status_code=500, detail="Database insertion failed.")

        job_data = {
            "job_id": job_id,
            "type": "upload_prompt",
            "reference_images": image_urls,
            "user_prompt": user_query,
            "user_id": user_id
        }
        await enqueue_job(job_data)
        logger.info(f"[Job Enqueued] {job_id} for user {user_id}")

        return UploadPromptRequest(
            user_query=user_query,
            reference_images=image_urls,
            remaining_credits=remaining_credits,
            job_id=job_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[Upload Prompt Error] Job {job_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while processing upload."
        )
