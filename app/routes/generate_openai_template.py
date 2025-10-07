from fastapi import APIRouter
from app.services.queue import enqueue_job

router = APIRouter()

# TODO: Refactor this to handle authentication and validation

@router.get("/generate_openai_template")
async def refine_prompts(job_id:str):
    """
    Generate image using openai.
    Enqueues image generation job for background processing.
    """
    job_data = {
        "type": "generate_openai_template",
        "job_id": job_id
    }
    await enqueue_job(job_data)
    return {"message": "Job enqueued for generating image using oepnai"}
