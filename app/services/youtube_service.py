import asyncio
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

async def fetch_top_videos(query: str, search_limit: int = 10) -> str:
    """
    Fetches the thumbnail URL of the YouTube video (non-Shorts) with the highest views for a query.
    """
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=os.getenv("YOUTUBE_API_KEY")
    )

    # Step 1: Search videos by query
    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=search_limit
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]
    if not video_ids:
        return None

    # Step 2: Fetch video statistics and content details
    stats_response = youtube.videos().list(
        part="statistics,contentDetails,snippet",
        id=",".join(video_ids)
    ).execute()

    # Step 3: Filter out Shorts (duration <= 60s)
    non_shorts = []
    for video in stats_response["items"]:
        duration = video["contentDetails"]["duration"]  # ISO 8601 format
        # Convert duration to seconds
        import isodate
        seconds = isodate.parse_duration(duration).total_seconds()
        if seconds > 60:
            non_shorts.append(video)

    if not non_shorts:
        return None

    # Step 4: Find the video with max views
    max_view_video = max(
        non_shorts,
        key=lambda x: int(x["statistics"].get("viewCount", 0))
    )

    print(
        "Max views video:", 
        max_view_video["snippet"]["title"], 
        max_view_video["statistics"].get("viewCount", 0)
    )
    return max_view_video["snippet"]["thumbnails"]["high"]["url"]



