import base64
import json
import requests
import os
from io import BytesIO
from PIL import Image
from google import genai
from dotenv import load_dotenv

load_dotenv()


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_thumbnail_system_prompt(refined_prompt: str, reference_image_urls: list, youtube_image_urls: list):
    """
    Builds a detailed system prompt for thumbnail generation.
    """

    # TODO: Refactor this prompt to be more concise and effective

    prompt = (
        "You are a professional YouTube thumbnail designer AI.\n\n"
        "🎯 Your goal: Generate a detailed design concept for a YouTube thumbnail that is visually striking, "
        "highly engaging, and optimized for clicks.\n\n"
        "🧠 Instructions:\n"
        "- Use the *refined prompt* below as the main theme.\n"
        "- Use the *reference images* to preserve the subject’s face and identity (do not change faces). "
        "Try to match ~90% of the face — avoid over-processing that makes it look artificial.\n"
        "- Use the *YouTube example images* only for inspiration (composition, layout, color, typography).\n"
        "- Suggest an ideal thumbnail layout: background, subject placement, title position, color palette, fonts, lighting, and contrast.\n"
        "- Make sure the design looks professional, high-quality, and platform-optimized.\n\n"
        f"📝 Refined Prompt:\n{refined_prompt}\n\n"
        "🧍 Reference Images (faces must remain unchanged):\n"
        "Don't make my face bigger than actual content you should keep it balanced main content is video you can go with 50-50 proprtion make it realistic and engaging not like some old scrappy template"
        "try to add icons based on the prompt\n"
        "Try to maintain asthetic in text use better backgrounds dont keep empty spaces make full use of it and try to add main topics icon "
        "try to use good color scehme and take refrence of text styles from youtube refrence images"
        "for eg:\n"
        "if the video is about python include python logo if it's abour docker include docker logo "
    )

    for i, url in enumerate(reference_image_urls):
        prompt += f"- Reference Image {i+1}: {url}\n"
    for i, item in enumerate(youtube_image_urls):
        # Extract the actual URL whether it's a dict or string
        url = item["thumbnail_url"] if isinstance(item, dict) else item
        print(url)
        prompt += f"- Example Image {i+1}: {url}\n"


    prompt += (
        "\nNow return a **detailed design plan** for the thumbnail. "
        "Describe the layout, title position and text, background design, color scheme, and style."
    )

    return prompt


def fetch_image_from_url(url: str) -> Image.Image:
    """
    Fetch an image from a signed URL and return it as a PIL Image.
    """
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


async def thumbnail_generation2(refined_prompt: str, reference_image_urls: list, youtube_image_urls: list):
    """
    Generates a thumbnail design concept using Gemini 2.5 Flash Image model
    with signed image URLs.
    """
    prompt_text = build_thumbnail_system_prompt(refined_prompt, reference_image_urls, youtube_image_urls)
    youtube_image_url= []

    for i, item in enumerate(youtube_image_urls):
        url = item["thumbnail_url"] if isinstance(item, dict) else item  
        youtube_image_url.append(url)

    all_images = []

    for url in reference_image_urls + youtube_image_url:
        try:
            all_images.append(fetch_image_from_url(url))
            print(f"✅ Fetched image from: {url}")
        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt_text] + all_images,
    )

    output_path = "generated_thumbnail.png"
    text_output = None
    for part in response.candidates[0].content.parts:
        if part.text:
            text_output = part.text
            print("📝 Design Plan:", text_output)
        elif part.inline_data:
            img = Image.open(BytesIO(part.inline_data.data))
            img.save(output_path)
            print(f"🖼️ Saved generated image to {output_path}")

    # TODO: return image url after generating an image


    return {
        "image_path": output_path,
    }
