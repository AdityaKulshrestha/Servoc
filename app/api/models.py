from pydantic import BaseModel
from typing import List

class PredictRequest(BaseModel):
    """Input schema for prediction endpoint"""
    input_vector: List[float]


class PredictResponse(BaseModel):
    """Output schema for prediction endpoint"""
    request_id: str
    prediction: List[float]
    latency_ms: float