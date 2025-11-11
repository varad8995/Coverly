import aiohttp
import hashlib
import json
import base64
import boto3
import base64
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from app.db.queue_connection import redis_conn

load_dotenv()

S3_BUCKET = os.getenv("S3_CACHED_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
s3 = boto3.client("s3", region_name="ap-south-1",    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com" )


async def compute_cache_key(prompt: str, ref_images: list, model_name: str):
    ref_hashes = []
    async with aiohttp.ClientSession() as session:
        for url in ref_images:
            async with session.get(url) as resp:
                if resp.status == 200:
                    img_bytes = await resp.read()
                    ref_hashes.append(hashlib.sha256(img_bytes).hexdigest())

    key_data = json.dumps({
        "model": model_name,
        "prompt": prompt,
        "ref_hashes": ref_hashes
    }, sort_keys=True)
    return hashlib.sha256(key_data.encode()).hexdigest()





async def upload_to_s3(image_base64: str, job_id: str) -> str:
    """
    Upload image to S3 (private) and return the key (used for presigned URL)
    """
    image_bytes = base64.b64decode(image_base64.split(",")[-1])
    filename = f"thumbnails/{job_id}_{int(datetime.now().timestamp())}.png"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=filename,
        Body=image_bytes,
        ContentType="image/png",
        ACL="private"  
    )
    return filename


def generate_presigned_url(s3_key: str, expires_in: int = 604800) -> str:
    """
    Generate a pre-signed URL valid for `expires_in` seconds
    """
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": S3_BUCKET, "Key": s3_key},
        ExpiresIn=expires_in
    )
    return url


async def upload_to_s3_bytes(image_bytes: bytes, job_id: str, count: int) -> str:
    key = f"thumbnails/{job_id}_{count}_{int(datetime.now().timestamp())}.png"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=image_bytes,
        ContentType="image/png",
        ACL="private"
    )
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=604800  
    )
    return url



def upload_base64_to_s3(image_base64: str, job_id: str) -> str:
    if image_base64.startswith("data:image"):
        image_base64 = image_base64.split(",")[-1]

    image_bytes = base64.b64decode(image_base64)
    key = f"thumbnails/{job_id}_{int(time.time())}.png"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=image_bytes,
        ContentType="image/png",
        ACL="private"
    )

    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=604800
    )
    return url, key



CHANNEL = "thumbnail_updates"

async def publish_job_update(
    job_id: str,
    status: str,
    progress: int | None = None,
    message: str | None = None,
    generated_images: list[str] | None = None
):
    """
    Publishes structured job updates to Redis for frontend real-time updates.
    """
    payload = {
        "job_id": job_id,
        "status": status,            
        "progress": progress,         
        "message": message,           
        "generated_images": generated_images or []  
    }

    await redis_conn.publish(CHANNEL, json.dumps(payload))
    print(f"[Worker] Published update: {payload}")
