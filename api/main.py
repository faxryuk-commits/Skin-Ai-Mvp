from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from schemas import AnalysisResult
from skin_analyzer import analyze_image


app = FastAPI(title="Skin AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze", response_model=AnalysisResult)
async def analyze(file: UploadFile = File(...), user_id: str = Form("anon")) -> AnalysisResult:
    image_bytes = await file.read()
    try:
        result = await analyze_image(image_bytes=image_bytes, user_id=user_id)
    except ValueError as exc:
        if str(exc) == "bad_quality":
            raise HTTPException(status_code=422, detail="bad_quality") from exc
        raise
    return AnalysisResult(**result)


@app.get("/health")
def health() -> dict:
    return {"ok": True}

