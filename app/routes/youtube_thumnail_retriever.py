
from fastapi import APIRouter
from ..services.queue import enqueue_job

router = APIRouter()


# TODO: Refactor this to handle authentication and validation
@router.get("/youtube/search")
async def search_youtube(title: str,job_id:str):
    """
    Enqueues a YouTube search job for background processing.
    """
    job_data = {
        "type": "youtube_search",
        "title": title,
        "id": job_id
    }
    await enqueue_job(job_data)
    return {"message": "Job enqueued for YouTube search", "title": title}
