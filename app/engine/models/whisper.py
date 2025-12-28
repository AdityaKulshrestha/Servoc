import torch
import numpy as np
from typing import List, Dict
from ..base import STTEngine
import logging

import intel_extension_for_pytorch as ipex
from transformers import WhisperForConditionalGeneration, WhisperProcessor


logger = logging.getLogger(__name__)


# Add a model registry
class WhisperSTTEngine(STTEngine):
    def __init__(self, config):
        super().__init__()
        self.config = config

    # Lightweight Constructor princple
    def load_model(self) -> None:
        """Loads whisper model and processor."""
        model_id = self.config.model_path or self.config.model_id

        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_id, 
        )
        # TODO: Think of abstraction here
        # processor_id = self.config.processor_id or model_id
        self.processor = WhisperProcessor.from_pretrained(model_id)
        self.tokenizer = self.processor.tokenizer
        self.sample_rate = self.processor.feature_extractor.sampling_rate

        # Move to device and set eval mode
        self.model = self.model.to(self.device)
        self.model.eval()

        # IPEX optimization
        self.model = ipex.optimize(self.model, dtype=torch.bfloat16)
        # self.model = torch.compile(self.model, backend="ipex")

        self._is_loaded = True
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded
    
    def _process_audio(self, audio_list: List[np.ndarray]) -> Dict[str, torch.Tensor]:
        """Process audio through Whisper feature extractor."""
        inputs = self.feature_extractor(
            audio_list,
            sampling_rate=self.sample_rate,
            return_tensors="pt",
            padding=True,
        )    

        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        return inputs
    
    def transcribe(self, inputs: np.ndarray, **kwargs):
        """
        Transcribes audio into text

        Args:
            inputs: Audio data as numpy array.
            **kwargs: Additional arguments for transcription.
        
        Returns:
            Transcribed text.
        """
        # Pads the input audio and converts to input features
        inputs_features = self.processor(inputs, sample_rate=self.sample_rate, return_tensors="pt").input_features
        with torch.no_grad(), torch.amp.autocast('cpu'):
            predicted_ids = self.model.generate(inputs_features)

        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return transcription

        



