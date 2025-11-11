
from fastapi import FastAPI, HTTPException,APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
from io import BytesIO

router = APIRouter()
class DownloadRequest(BaseModel):
    presigned_url: str

@router.post("/download-photo/")
def download_photo(request: DownloadRequest):
    """
    Download a photo from a given AWS S3 presigned URL (provided in the request body)
    and return it as a downloadable file.
    """
    try:
        response = requests.get(request.presigned_url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download file from presigned URL")

        filename = "downloaded_photo"
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition and "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[-1].strip('"')

        content_type = response.headers.get("Content-Type", "application/octet-stream")

        return StreamingResponse(
            BytesIO(response.content),
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file: {str(e)}")