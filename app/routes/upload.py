from fastapi import APIRouter, Form, File, UploadFile, HTTPException, status
from typing import List, Optional
from ..services.queue import enqueue_job
from ..db.s3_storage import upload_to_s3
from ..db.supabase_client import supabase
from ..models.upload_prompt import UploadPromptRequest
import uuid
import logging
import asyncio

logger = logging.getLogger("coverly.api")
router = APIRouter()


@router.post(
    "/upload-prompt",
    response_model=UploadPromptRequest,
    status_code=status.HTTP_201_CREATED,
    summary="Upload prompt and reference images",
    description="Uploads reference images to S3, saves metadata to Supabase, and enqueues the thumbnail generation job."
)
async def upload_prompt_with_images(
    user_query: Optional[str] = Form(None),
    aspect_ratio: Optional[str] = Form("16:9"),
    platform: Optional[str] = Form("YouTube"),
    reference_images: Optional[List[UploadFile]] = File(None),
    
):
    job_id = str(uuid.uuid4())
    image_urls: List[str] = []

    try:
        if reference_images:
            upload_tasks = [
                upload_to_s3(job_id, img.file, img.filename, img.content_type or "image/jpeg")
                for img in reference_images
            ]
            results = await asyncio.gather(*upload_tasks, return_exceptions=True)

            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    logger.error(f"[Upload Error] {reference_images[i].filename}: {res}")
                    continue
                if res:
                    image_urls.append(res)

        if not user_query and not image_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must provide either a text prompt or at least one reference image."
            )

        record = {
            "job_id": job_id,
            "user_query": user_query,
            "reference_images": image_urls or [],
            "aspect_ratio": aspect_ratio,    
            "platform": platform,   
            "status": "queued",
        }

        response = supabase.table("thumbnail_prompts").insert(record).execute()
        if not response.data:
            logger.error(f"[Supabase Error] Failed to insert job {job_id}")
            raise HTTPException(status_code=500, detail="Database insertion failed.")

        job_data = {
            "id": job_id,
            "type": "upload_prompt",
            "reference_images": image_urls,
            "user_prompt": user_query,
        }

        await enqueue_job(job_data)
        logger.info(f"[Job Enqueued] {job_id}")

        return UploadPromptRequest(
            user_query=user_query,
            reference_images=image_urls
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[Upload Prompt Error] Job {job_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while processing upload."
        )
