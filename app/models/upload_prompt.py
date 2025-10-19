from pydantic import BaseModel, Field
from typing import List, Optional

class UploadPromptRequest(BaseModel):
    user_query: Optional[str] = Field(None, description="The user's text prompt for thumbnail generation")
    reference_images: Optional[List[str]] = Field(
        default_factory=list,
        description="List of reference image URLs (optional)"
    )
