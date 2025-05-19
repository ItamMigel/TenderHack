from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import torch
from translation import TranslationModel
import time

# Initialize the model once on startup
print("Loading translation model...")
translator = None

# Check if CUDA is available
if torch.cuda.is_available():
    translator = TranslationModel()
    print("✨ Translation model successfully loaded on GPU ✨")
else:
    print("No GPU available. Translation may be slow.")
    translator = TranslationModel()
    print("✨ Translation model successfully loaded on CPU ✨")

app = FastAPI(title="Translation API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class TranslationResponse(BaseModel):
    translated_text: str
    processing_time: float

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text from source language to target language.
    
    Parameters:
    - text: Text to translate
    - source_language: Source language (e.g., "Russian", "English")
    - target_language: Target language (e.g., "English", "Russian")
    
    Returns:
    - translated_text: Translated text
    - processing_time: Translation processing time in seconds
    """
    if not translator:
        raise HTTPException(status_code=500, detail="Translation model not initialized")
    
    try:
        if torch.cuda.is_available():
            start_time = torch.cuda.Event(enable_timing=True)
            end_time = torch.cuda.Event(enable_timing=True)
            start_time.record()
            
            translated_text = translator.translate(
                request.text,
                request.source_language,
                request.target_language
            )
            
            end_time.record()
            torch.cuda.synchronize()
            processing_time = start_time.elapsed_time(end_time) / 1000.0  # Convert to seconds
        else:
            start_time = time.time()
            
            translated_text = translator.translate(
                request.text,
                request.source_language,
                request.target_language
            )
            
            processing_time = time.time() - start_time
            
        return TranslationResponse(
            translated_text=translated_text,
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Translation API is running. Use /translate endpoint for translation."}

if __name__ == "__main__":
    uvicorn.run("translation_api:app", host="0.0.0.0", port=8000, reload=False) 