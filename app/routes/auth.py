from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
REDIRECT_URL = os.getenv("REDIRECT_URL")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

router = APIRouter()

@router.get("/login")
def login():
    """
    Redirect user to Google sign-in via Supabase Auth.
    """
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": REDIRECT_URL}
    })
    return RedirectResponse(res.url)


@router.get("/callback")
def callback():
    """
    After Google login, Supabase redirects here.
    The access token will be in frontend.
    """
    return JSONResponse({
        "message": "Login successful! Copy your access_token from frontend to call APIs."
    })


@router.post("/add-thumbnail")
async def add_thumbnail(request: Request, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "").strip()
    user_res = supabase.auth.get_user(jwt=token)

    if not user_res.user:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user_res.user.id
    body = await request.json()

    data = {
        "user_id": user_id,
        "title": body.get("title"),
        "base_prompt": body.get("base_prompt"),
        "refined_prompt": body.get("refined_prompt"),
        "youtube_examples": body.get("youtube_examples", []),
        "reference_images": body.get("reference_images", []),
        "generated_images": body.get("generated_images", []),
    }

    res = supabase.table("thumbnail_prompts").insert(data).execute()
    return {"message": "Thumbnail saved ✅", "data": res.data}


@router.get("/my-thumbnails")
def get_my_thumbnails(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "").strip()
    user_res = supabase.auth.get_user(jwt=token)

    if not user_res.user:
        raise HTTPException(status_code=401, detail="Invalid token")

    res = supabase.table("thumbnail_prompts").select("*").execute()
    return res.data
