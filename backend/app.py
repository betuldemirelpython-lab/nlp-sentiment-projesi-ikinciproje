#backend/app.py
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load local environment variables (.env)
load_dotenv()

app = FastAPI(title="AI Sentiment Analysis API")

# Lazy-loaded tokenizer and model to avoid hard failures at import time
tokenizer = None
model = None

# Get API key from environment variables
API_KEY = os.getenv("API_KEY")

class TextRequest(BaseModel):
    text: str


def load_model():
    """Load tokenizer and model into module-level variables using PyTorch.
    Uses 'savasy/bert-base-turkish-sentiment-cased' which is fine-tuned for Turkish sentiment analysis.
    """
    global tokenizer, model
    try:
        model_name = "savasy/bert-base-turkish-sentiment-cased"
        logger.info(f"Loading tokenizer and model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        logger.info("Model and tokenizer loaded successfully")
    except Exception as e:
        logger.exception(f"Failed to load model/tokenizer: {e}")
        tokenizer = None
        model = None


@app.on_event("startup")
def on_startup():
    load_model()


@app.get("/health")
def health():
    return {
        "status": "healthy" if (tokenizer is not None and model is not None) else "unhealthy",
        "model_loaded": tokenizer is not None and model is not None
    }


@app.post("/predict")
def predict(
    request: TextRequest,
    x_api_key: str = Header(...)
):
    # Enforce API key only if one is configured in .env
    if API_KEY:
        if not x_api_key or x_api_key != API_KEY:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: Invalid API Key"
            )

    if tokenizer is None or model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Check server logs for details."
        )

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    try:
        inputs = tokenizer(
            request.text,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)

        # In sst-2: label 0 is NEGATIVE, label 1 is POSITIVE
        negative_prob = float(probs[0][0])
        positive_prob = float(probs[0][1])

        return {
            "negative": negative_prob,
            "positive": positive_prob
        }
    except Exception as e:
        logger.exception(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Prediction error. See server logs for details."
        )