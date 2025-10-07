from fastapi import APIRouter
from app.services.queue import enqueue_job

router = APIRouter()

# TODO: Refactor this to handle authentication and validation

@router.get("/prompt/refine")
async def refine_prompts(prompt: str,job_id:str):
    """
    Refine user query into a more specific prompt using LLM.
    Enqueues a prompt refinement job for background processing.
    """
    job_data = {
        "type": "prompt_refinement",
        "user_query": prompt,
        "job_id": job_id
    }
    await enqueue_job(job_data)
    return {"message": "Job enqueued for refining prompts", "title": prompt}
