import logging
import time
import torch
from typing import Optional

from app.config import EngineConfig
from app.engine.model_loader import load_model

logger = logging.getLogger(__name__)


class InferenceEngine:
    """
    Inference engine for loading model and performing inference
    """

    def __init__(self, config: EngineConfig):
        self.config = config
        self.model = None
        self._initialized = False


    def initialize(self):
        """Initialize the engine and load model"""

        if self._initialized:
            return
        
        logger.info("Initializing inference engine")

        # TODO: Load the actual model here
        self.model = load_model(self.config)

        self._initialized = True
        logger.info("Inference engine intialized")

    
    def infer(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Run inference on the batched inputs.

        Args:
            inputs: Batched input tensor of shape [batch_size, ...]
        
        Returns:
            Outputs tensor of shape [batch_size, ...]
        """

        if not self._initialized:
            raise RuntimeError("Inference engine is not initialized")
        
        batch_size = len(inputs)
        logger.info(f"Running inference on batch size: {batch_size}")
        
        response = self.model.transcribe(inputs)
        
        return response
    

    def shutdown(self):
        """Shutdown the inference engine and release resources"""
        logger.info("Shutting down inference engine")
        self.model = None
        self._initialized = False