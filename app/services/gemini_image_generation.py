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



def build_thumbnail_system_prompt(refined_prompt: str):
    """
    Builds a detailed system prompt for thumbnail generation.
    """

    # TODO: Refactor this prompt to be more concise and effective

    prompt = (
        f"""
        You are a professional YouTube thumbnail designer AI.

        Your goal:
        Generate a detailed design concept for a high-quality, professional YouTube thumbnail with the goal of maximizing click-through rates. Use the refined prompt provided as the main theme for the design. Follow these instructions:


        example :

        If user prompt is "Create a thumbnail for a docker tutorial video for beginners"
        Then the thumbnail should include :
        Create a modern and professional tech logo inspired by the Docker branding.
            The logo should feature a minimalist whale icon carrying stacked shipping containers, symbolizing containerization and DevOps.
            Use a blue color palette similar to the official Docker colors:

            Background: dark navy or gradient black-blue

            Whale: light blue to medium blue

            Containers: slightly lighter or white-blue tones
            Include clean flat design, soft shadows, and rounded shapes for a friendly and modern look.
            Typography (if included): bold sans-serif, white or light yellow text, e.g. “Docker” or “Containerization”.
            The style should look like a tech tutorial thumbnail logo, suitable for YouTube — clean, professional, and easy to read on dark background.
            Composition: whale centered or slightly to the right, with text on left or bottom.
            Output as transparent background or dark gradient background.

        Guidelines:
            1. Incorporate the subject from the reference images while preserving their facial identity (~90% match), avoiding over-processing that renders the face unnatural.
            2. Use YouTube example images for layout, composition, color palette, typography, and inspiration.
            3. Suggest a layout featuring balanced proportions; ensure the face and main content occupy equal focus (~50-50 proportion).
            4. Add relevant icons based on the prompt theme (e.g., Python logo for Python-related videos, Docker logo for Docker-related content).
            5. Provide guidelines for the color scheme and background; ensure the design does not have empty spaces and uses text styles effectively.
            6. Try to maintain an aesthetic that aligns with popular YouTube thumbnails.
            7. Try to make most out of the refined prompt and include all the important aspects in the thumbnail
            8. Give a detailed description of placement for elements including title position and text, fonts, background design, lighting, and contrast.
            9. Standard YouTube aspect ratio of 1280 x 720 pixels.
            10. Dont change the face of the person in the reference image try to match 100 percent of face don't overdo anything otherwise it will look like a generated image.
            11. Use more logos and icons related to the prompt to make it more attractive.
        Refined Prompt:
        {refined_prompt}

        Include reference images:

        Explore example images:

        Return a comprehensive design describing the layout, title position, text, background design, color scheme, and overall style.



        """)
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
    prompt_text = build_thumbnail_system_prompt(refined_prompt)
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
