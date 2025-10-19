import boto3
import os
import logging
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("coverly.s3")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
    logger.warning("⚠️ Missing AWS credentials or S3 bucket name!")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
)


async def upload_to_s3(job_id: str, file_obj, filename: str, content_type: str = "image/jpeg"):
    """
    Upload a file object to S3 and return a presigned URL.
    Ensures file data is read safely and logged properly.
    """
    try:
        if not S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME environment variable is not set.")
        if not filename:
            raise ValueError("Missing filename for upload.")
        if file_obj is None:
            raise ValueError("File object is None.")

        file_obj.seek(0)
        file_bytes = file_obj.read()
        if not file_bytes:
            raise ValueError(f"File '{filename}' is empty or unreadable.")

        file_key = f"{job_id}/{filename}"

        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_key,
            Body=file_bytes,
            ContentType=content_type,
        )

        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": file_key},
            ExpiresIn=60 * 60 * 24 * 7,  # 1 week
        )

        logger.info(f"[S3 Upload ✅] {filename} uploaded successfully.")
        return signed_url

    except (NoCredentialsError, ClientError, ValueError, Exception) as e:
        logger.error(f"[S3 Upload ❌] {filename or 'unknown'} failed: {e}")
        return None
