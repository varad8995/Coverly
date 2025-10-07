from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

async def fetch_top_videos(query: str, max_results: int = 5) -> list:
    """
    Fetches top YouTube videos template urls based on a search query.
    """
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=os.getenv("YOUTUBE_API_KEY"))
    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    ).execute()
    
    videos = []
    for item in search_response["items"]:
        videos.append({
            "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
        })
    
    return videos
