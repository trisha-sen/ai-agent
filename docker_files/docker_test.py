from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Test FastAPI App")


class PredictRequest(BaseModel):
    features: list[float]


class PredictResponse(BaseModel):
    prediction: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    prediction = sum(request.features)
    return PredictResponse(prediction=prediction)
