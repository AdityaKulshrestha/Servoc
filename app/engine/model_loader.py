import logging 
from typing import Any, Optional
from pathlib import Path
from app.config import EngineConfig
from app.engine.models.whisper import WhisperSTTEngine

logger = logging.getLogger(__name__)


def load_model(config: EngineConfig) -> Any:
    """
    Load a model from disk
    """

    # TODO: Add registry based model loading
    if config.model_path is None:
        raise ValueError("No model path provided")
    
    # TODO: Implement actual model
    if config.model_type.lower() == "whisper":
        engine = WhisperSTTEngine(config)
        engine.load_model()
        return engine

    raise NotImplementedError("Model loading not implemented")