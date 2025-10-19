from openai import OpenAI
from ..utils.system_prompts import build_thumbnail_system_prompt_openai
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def thumbnail_generation(refined_prompt: str, reference_images, youtube_reference_images):

    system_prompt = build_thumbnail_system_prompt_openai(refined_prompt)
    response = client.responses.create(
        model="gpt-4.1",
        input=[

            {
            "role": "system",
            "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": refined_prompt},
                    {"type": "input_image", "image_url": reference_images[0]},
                ],
            }
        ],
        tools=[{"type": "image_generation"}],
    )

    image_generation_calls = [
        output for output in response.output if output.type == "image_generation_call"
    ]

    if image_generation_calls:
        image_base64 = image_generation_calls[0].result
        print("Image generated successfully.")
        return image_base64
    else:
        print("No image generated:", response.output)


