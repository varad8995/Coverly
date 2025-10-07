from fastapi import APIRouter
from app.services.queue import enqueue_job

router = APIRouter()


# TODO: Refactor this to handle authentication and validation

@router.get("/generate_gemini_template")
async def refine_prompts2(job_id:str):
    """
    Generate image using gemini.
    Enqueues a template generation job for background processing.
    """
    job_data = {
        "type": "generate_gemini_template",
        "job_id": job_id
    }
    await enqueue_job(job_data)
    return {"message": "Job enqueued for generating image using gemini",}
