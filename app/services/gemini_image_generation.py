import base64
import io
import requests
import os
import asyncio
import httpx
from PIL import Image
from io import BytesIO
from io import BytesIO
from PIL import Image
from google import genai
from dotenv import load_dotenv
from ..utils.helper import upload_to_s3_bytes
from ..utils.system_prompts import build_thumbnail_system_prompt_gemini
load_dotenv()


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))



async def fetch_image(url: str) -> Image.Image:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content))

async def fetch_all_images(urls: list) -> list:
    tasks = [fetch_image(url) for url in urls]
    return await asyncio.gather(*tasks)



def pil_to_inline_data(image: Image.Image, mime_type="image/jpeg"):
    """
    Convert a PIL Image into Gemini-compatible inline_data.
    """
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    return {
        "mime_type": mime_type,
        "data": buffer.getvalue()
    }

async def thumbnail_generation_gemini(refined_prompt: str, reference_image_urls: list, youtube_image_urls: list,job_id: str):
    prompt_text = build_thumbnail_system_prompt_gemini()


    if not isinstance(youtube_image_urls, list):
        youtube_image_urls = [youtube_image_urls]

    all_urls = reference_image_urls + [
        item["thumbnail_url"] if isinstance(item, dict) else item
        for item in youtube_image_urls
    ]
    print(all_urls)
    images = await fetch_all_images(all_urls)
    
    presenter_image = images[0]
    ref_image1 = images[1] if len(images) > 1 else presenter_image

    presenter_inline = pil_to_inline_data(presenter_image)
    ref1_inline = pil_to_inline_data(ref_image1)
    if presenter_inline:
        response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt_text + refined_prompt + """
                                Interpret the images as follows:
                                - Image 1: Presenter’s face — must stay identical. 
                                - Images 2+: Reference layout/style only.
                            """},
                            {"inline_data": presenter_inline},
                            {"inline_data": ref1_inline},
                        ]
                    }
                ]
            )
    else:
        response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt_text + refined_prompt + """
                            """}
                        ]
                    }
                ]
            )


    output_urls = []
    count = 1
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            img_bytes = part.inline_data.data
            url = await upload_to_s3_bytes(img_bytes, job_id, count)
            output_urls.append(url)
            count += 1

    return {"image_urls": output_urls}
