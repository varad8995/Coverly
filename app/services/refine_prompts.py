from openai import OpenAI
from dotenv import load_dotenv
import os 
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def refine_prompt(user_prompt:str) -> str:
    prompt = f"""
    Your task is to refine the following user prompt to make it clearer and more effective for achieving the intended task. The refinement should focus on enhancing clarity, incorporating necessary details, and specifying task-specific requirements.

    Original Prompt:
    {user_prompt}

    Guidelines for Refinement:

    Ensure that the task is clearly defined and easy to understand;
    Add specific details or context to increase relevance;
    Specify any steps required to complete the task, if applicable;
    Provide an example or template to guide the desired output format.
    Please begin with your refinement according to these guidelines.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()



async def extarct_title(user_prompt: str) -> str:
    prompt = f"""
    You are an ai assistant who is expert in creating catchy and trending youtube titles.
    Your task is to transform the given video context or description into a catchy YouTube video title that maximizes search performance and click-through rate.

    The context/description for the video is provided below, surrounded by curly braces:
    
    User prompt:
    "{user_prompt}"

    and turn it into a catchy YouTube video title 
    that would perform well in search and click-through rate.
    Respond with only the title.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()
