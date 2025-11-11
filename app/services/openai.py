from openai import OpenAI
from ..utils.system_prompts import build_thumbnail_system_prompt_openai
from ..utils.image_utils import prepare_image_for_openai
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def thumbnail_generation(refined_prompt: str, reference_images, youtube_reference_images,aspect_ratio,platform):

    system_prompt = build_thumbnail_system_prompt_openai(refined_prompt,aspect_ratio,platform)
    if reference_images:
        prepared = prepare_image_for_openai(reference_images[0])
        if prepared:
            if prepared.startswith("http"):
                image_input = {"type": "input_image", "image_url": prepared}
            else:
                image_input = {"type": "input_image", "image_url": f"data:image/jpeg;base64,{prepared}"}
    response = client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "system",
                        "content": [
                            {"type": "input_text", "text": system_prompt}
                        ],
                    },
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": refined_prompt},
                                image_input,
                            ],
                        },
                    ],
                tools=[{"type": "image_generation"}],
            )

            # Handle tool output
    image_generation_calls = [
        output for output in response.output if output.type == "image_generation_call"
    ]

    if image_generation_calls:
        image_base64 = image_generation_calls[0].result
        print("✅ Image generated successfully.")
        return image_base64
    else:
        print("⚠️ No image generated:", response.output)
        return None



