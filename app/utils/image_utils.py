import re
import base64
import requests
from typing import Union

# Matches S3 presigned URLs like:
# https://s3.<region>.amazonaws.com/<bucket>/<key>?X-Amz-Algorithm=...
S3_PRESIGNED_PATTERN = re.compile(r"https:\/\/s3[.-].*\.amazonaws\.com\/.*X-Amz-Algorithm=")


def prepare_image_for_openai(image_url_or_path: str, timeout: int = 10) -> Union[str, None]:
    """
    Convert a presigned S3 URL (or local file) into a base64 string suitable for OpenAI input.

    Args:
        image_url_or_path: The S3 presigned URL or local file path.
        timeout: Max download timeout in seconds.
    Returns:
        Base64-encoded image string, or None if failed.
    """
    try:
        if not image_url_or_path:
            return None

        # --- Case 1: S3 presigned URL ---
        if S3_PRESIGNED_PATTERN.match(image_url_or_path):
            print(f"[prepare_image_for_openai] Detected presigned S3 URL → converting to base64")
            resp = requests.get(image_url_or_path, timeout=timeout)
            resp.raise_for_status()
            return base64.b64encode(resp.content).decode("utf-8")

        # --- Case 2: Local file path ---
        elif image_url_or_path.startswith("/") or image_url_or_path.startswith("./"):
            print(f"[prepare_image_for_openai] Detected local file → converting to base64")
            with open(image_url_or_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")

        # --- Case 3: Already public URL ---
        else:
            print(f"[prepare_image_for_openai] Public URL → pass through")
            return image_url_or_path

    except Exception as e:
        print(f"[prepare_image_for_openai] Failed to process image {image_url_or_path}: {e}")
        return None
