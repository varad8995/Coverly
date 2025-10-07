from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
import base64
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_thumbnail_system_prompt(refined_prompt: str, reference_images_base64: list, youtube_images_base64: list):
    """
    Builds a single system prompt for the AI with all context embedded.
    """

    # TODO: Refactor this prompt to be more concise and effective

    prompt = (
        "You are a professional YouTube thumbnail designer AI.\n\n"
        "🎯 Your goal: Generate a detailed design concept for a YouTube thumbnail that is visually striking, "
        "highly engaging, and optimized for clicks.\n\n"
        "🧠 Instructions:\n"
        "- Use the *refined prompt* below as the main theme.\n"
        "- Use the *reference images* to preserve the subject’s face and identity (do not change faces).Try to match 90 percent of face don't over do anything otherw3ise it will look like generated image  \n"
        "- Use the *YouTube example images* only for inspiration (composition, layout, color, typography).\n"
        "- Suggest an ideal thumbnail layout: background, subject placement, title position, color palette, fonts, lighting, and contrast.\n"
        "- Make sure the design looks professional, high-quality, and platform-optimized.\n\n"
        f"📝 Refined Prompt:\n{refined_prompt}\n\n"
        "🧍 Reference Images (faces must remain unchanged):\n"
    )

    for i, url in enumerate(reference_images_base64):
        prompt += f"- Reference Image {i+1}: {url}\n"

    # for i, url in enumerate(youtube_images_base64):
    #     prompt += f"- Example Image {i+1}: {url}\n"


    prompt += (
        "\nNow return a **detailed design plan** for the thumbnail. "
        "Describe the layout, title position and text, background design, color scheme, and style."
    )
    print(prompt)
    return prompt


# TODO: Refactor this remove hardcoded image path and pass actual images

local_filename= "/Users/varadbhalsing/Documents/AI-thumbnail-generator/Coverly/app/services/varad.jpeg"

with open(local_filename, "rb") as image_file:
    image_bytes = image_file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    print("Image successfully converted to base64!")

async def thumbnail_generation(refined_prompt: str, reference_images, youtube_reference_images):

    prompt_text = build_thumbnail_system_prompt(refined_prompt, reference_images, youtube_reference_images)

    # TODO: Refactor this to handle multiple images and pass them correctly to the API

    response = client.images.edit(
        model="gpt-image-1",
        image=open("/Users/varadbhalsing/Documents/AI-thumbnail-generator/Coverly/app/services/varad.jpeg", "rb"),     
        prompt=prompt_text,  
        size="1024x1024",
        input_fidelity="high",
        mask= open("/Users/varadbhalsing/Documents/AI-thumbnail-generator/Coverly/app/services/varad.jpeg", "rb"),     

    )
    output_data = {
    "full_response": str(response), 
    "image_url": response.data[0].url
}

    with open("image_response.json", "w") as json_file:
        json.dump(output_data, json_file, indent=4)
        print(response.data[0].url)
        return response.data[0].url
