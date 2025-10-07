from fastapi import FastAPI
from app.routes import generate_gemini_template, generate_openai_template, refine_use_query, upload , youtube_thumnail_retriever

app = FastAPI(
    title="Coverly API",
    description="Backend API for generating AI thumbnails with YouTube reference search.",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "up and running 🚀"}


app.include_router(refine_use_query.router, prefix="/api", tags=["User Query"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(youtube_thumnail_retriever.router, prefix="/api", tags=["Youtube"])
app.include_router(generate_openai_template.router, prefix="/api", tags=["Generate Template"])
app.include_router(generate_gemini_template.router, prefix="/api", tags=["Generate Template"])