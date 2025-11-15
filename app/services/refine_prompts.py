from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@traceable(
    name="OpenAI Prompt Refinement",
    metadata={"model": "gpt-4.1-mini", "tool": "refine_prompt"}
)

async def refine_prompt(user_prompt: str,aspect_ratio=str,platform=str) -> str:
    """
    Refines a user-provided prompt to make it clearer, more detailed, and actionable.
    Ensures any reference images are respected (faces unchanged).
    """
    prompt = f"""
    You are an AI assistant specialized in refining prompts for maximum clarity and effectiveness.

    Original Prompt:
    {user_prompt}
    {aspect_ratio}
    {platform}
    Guidelines:
    - Make the task clearly defined and easy to understand.
    - Preserve any reference images exactly (do not alter faces or main elements).
    - Add necessary context or details to increase relevance.
    - Specify steps if applicable.
    - Use futuristic, high-contrast tech color palettes:
        - neon cyan + deep navy, purple + electric blue, teal + black, lime + charcoal, blue + white. , white + yellow 
        - Title: 3–5 bold, modern tech words, using clean sans-serif fonts (Inter, Montserrat, Poppins, SF Pro).
    - Use best Font's with good colour scehme anf styling
    - Keep ALL text, graphics, icons, subjects, and visual elements fully inside the template boundaries. NOTHING should be cropped, clipped, or cut off.
    - Leave comfortable padding on all sides.
    - Provide an example or template for the desired output format.

    Refine the original prompt following these guidelines.
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


@traceable(
    name="OpenAI {platform} Title Generation",
    metadata={"model": "gpt-4.1-mini", "tool": "extract_title"}
)
async def extract_title(video_context: str,platform=str) -> str:
    """
    Generates a catchy, SEO-optimized  title from a video description or context.
    Returns only the title.
    """
    prompt = f"""
    You are an expert AI in creating trending and clickable {platform} titles.

    Video Context:
    "{video_context}"

    Generate a catchy, search-optimized {platform} title that maximizes click-through rate.
    Respond with **only the title**.
    it should look like a professional {platform} title.
    Should be short and engaging.
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
