from pydantic import BaseModel
from typing import List, Optional

# DEPRECATED
# class PredictRequest(BaseModel):
#     """Input schema for prediction endpoint"""
#     input_vector: List[float]

# DEPRECATED
# class PredictResponse(BaseModel):
#     """Output schema for prediction endpoint"""
#     request_id: str
#     prediction: List[float]
#     latency_ms: float

class TranscriptionResponse(BaseModel):
    """OpenAI Transcription response schema"""
    text: str
    usage: dict


# DEPRECATED
# class TranscriptionRequest(BaseModel):
#     """OpenAI Transcription request schema"""
#     model: str
#     chunking_strategy: str = "auto"
#     include: List
#     known_speaker_names: Optional[List]
#     known_speaker_references: Optional[List]
#     language: Optional[str]
#     prompt: Optional[str]
#     response_format: Optional[str]
#     stream: Optional[bool]
#     temperature: Optional[int]
#     timestamp_granularities: Optional[List]
