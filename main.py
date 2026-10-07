from pathlib import Path
import io

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from .analyzer import analyze
from .models import AnalyzeRequest, AnalyzeResponse

app = FastAPI(
    title="TrustGuard NG API",
    version="0.1.0",
    description="AI-assisted scam and suspicious-message analyzer.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to the deployed frontend domain before production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "TrustGuard NG",
        "status": "online",
        "message": "Think before you click. Verify before you pay.",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_text(payload: AnalyzeRequest):
    return analyze(payload.text)


@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image.")

    content = await file.read()
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be smaller than 8 MB.")

    try:
        image = Image.open(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.") from exc

    extracted_text = ""
    try:
        import pytesseract
        extracted_text = pytesseract.image_to_string(image).strip()
    except Exception:
        extracted_text = ""

    if not extracted_text:
        return {
            "ocr_available": False,
            "message": "Image received, but OCR is unavailable or no readable text was found.",
            "next_step": "Install the Tesseract OCR engine or use the text analyzer.",
        }

    return {
        "ocr_available": True,
        "extracted_text": extracted_text,
        "analysis": analyze(extracted_text),
    }
