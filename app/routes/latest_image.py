from fastapi import FastAPI, HTTPException, status
from supabase import create_client, Client
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from ..db.supabase_client import supabase
import uuid
import logging
import asyncio

logger = logging.getLogger("coverly.api")
router = APIRouter()

    


class ImageLinkResponse(BaseModel):
    """Defines the structure of the successful response."""
    user_id: str = Field(..., description="The UUID of the user queried.")
    image_links: List[str] = Field(..., description="A list of unique image URLs.")
    count: int = Field(..., description="The number of unique image links returned.")


# --- Core Logic Function (Modified for error handling) ---
def fetch_latest_image_links(user_id: str, limit: int = 3) -> List[str]:
    """
    Fetches the latest 'limit' rows for a user and extracts all image links.
    (This is your original core logic, wrapped to raise exceptions.)
    """
    try:
        response = supabase.table('thumbnail_prompts')\
            .select('generated_images, generated_images_gemini')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()

        data = response.data
        if not data:
            return []

        all_image_links: List[str] = []

        for row in data:
            for column_name in ['generated_images', 'generated_images_gemini']:
                images_json: Optional[List[Dict]] = row.get(column_name)

                if isinstance(images_json, list):
                    for image_info in images_json:
                        # Assumes 'url' key or direct string link, as per your original logic
                        if isinstance(image_info, dict) and 'url' in image_info:
                            all_image_links.append(image_info['url'])
                        elif isinstance(image_info, str):
                             all_image_links.append(image_info)

        return list(set(all_image_links))

    except Exception as e:
        # Raise a 500 Internal Server Error for database issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(e)}"
        )


# --- FastAPI Endpoint ---

@router.get(
    "/users/{user_id}/latest-images",
    response_model=ImageLinkResponse,
    summary="Get the latest generated image links for a user"
)
async def get_latest_user_images(
    user_id: str, 
    limit: int = 3 # Use query parameter for flexibility
):
    """
    Retrieves the unique image URLs generated across the user's latest N prompt jobs.
    
    - **user_id**: The UUID of the user to query.
    - **limit**: The number of latest jobs (rows) to check (default is 3).
    """
    
    links = fetch_latest_image_links(user_id, limit)
    
    if not links:
        # Return 404 if no data is found for the user/query
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No image links found for user ID: {user_id} in the latest {limit} jobs."
        )

    return ImageLinkResponse(
        user_id=user_id,
        image_links=links,
        count=len(links)
    )