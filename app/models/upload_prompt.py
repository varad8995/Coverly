from pydantic import BaseModel, Field
from typing import List, Optional

class UploadPromptRequest(BaseModel):
    user_query: Optional[str] = Field(None, description="The user's text prompt for thumbnail generation")
    reference_images: Optional[List[str]] = Field(
        default_factory=list,
        description="List of reference image URLs (optional)"
    )
    remaining_credits: int = Field(..., description="User's remaining credits after this upload")
    job_id: str = Field(..., description="Unique identifier for the thumbnail generation job")
    user_id: str = Field(..., description="The UUID of the user uploading the prompt")
