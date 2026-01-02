import os
import torch
import numpy as np
from typing import List, Dict
from ..base import STTEngine
import logging

import subprocess
import fairseq
import torch.nn.functional as F
import torchaudio.sox_effects as ta_sox
import intel_extension_for_pytorch as ipex


logger = logging.getLogger(__name__)

# Register safe globals for torch serialization: _pickle.UnpicklingError: Weights only load failed. This file can still be loaded, to do so you have two options, do those steps only if you trust the source of the checkpoint
torch.serialization.add_safe_globals([fairseq.data.dictionary.Dictionary])


# Add a model registry
class Wav2Vec2STTEngine(STTEngine):
    def __init__(self, config):
        super().__init__()
        self.config = config

    # Lightweight Constructor principle
    def load_model(self) -> None:
        """Loads Wav2Vec2 model and processor"""

        self.effects = [["gain", "-n"]]

        if not os.path.exists(self.config.model_path):
            self._download_model(self.config.model_path, self.config.language)
        else:
            logger.info(f"Model found at {self.config.model_path}")

        self.model, self.cfg, self.task = fairseq.checkpoint_utils.load_model_ensemble_and_task([self.config.model_path])
        self.model = self.model[0]
        self.sample_rate = self.cfg.task.sample_rate

        self.dtype = torch.bfloat16 if self.config.dtype != "float32" else torch.float32
        self.model.to(self.dtype).eval()

        self.token = self.task.target_dictionary

        self._is_loaded = True


    def _download_model(self, model_path: str, language: str = "hindi"):
        """
        Checks if the model is downloaded and downloads it if not present
        """

        # TODO: Replace with a better method
        url = (
            "https://asr.iitm.ac.in/SPRING_INX/models/fine_tuned/"
            f"SPRING_INX_ccc_wav2vec2_{language.capitalize()}.pt"
        )

        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        if os.path.exists(model_path):
            logger.info(f"Model already exists: {model_path}")
            return
        
        subprocess.run(["wget", url, "-O", model_path], check=True)

        logger.info(f"Downloaded model to: {model_path}")

    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded
    

    def _process_audio(self, audio_list: List[np.ndarray]) -> Dict[str, torch.Tensor]:
        """Process audio for transcription"""
        audio_processed, rate = ta_sox.apply_effects_tensor(
            torch.tensor(audio_list), self.sample_rate, self.effects
        )
        return audio_processed.to(self.dtype)

    def transcribe(self, inputs: np.ndarray, **kwargs): 
        """
        Transcribe audio into text

        Args:
            inputs (np.ndarray): Audio input array
            **kwargs: Additional keyword arguments

        Returns:
            Transcription result
        """

        # Pads the input audio and convertsthe input features
        audio_tensor = self._process_audio(inputs)

        # Generate logits
        predicted_ids = self._generate_logits(audio_tensor)

        # Decode the logits to text
        transcriptions = self._decode_logits(predicted_ids)

        return transcriptions

    def _generate_logits(self, audio_inputs: torch.Tensor) -> torch.Tensor:
        """Generates logits from audio input"""
        with torch.no_grad():
            audio_processed = F.layer_norm(audio_inputs, audio_inputs.shape)

            logits = self.model(source=audio_processed, padding_mask=None)['encoder_out']
            predicted_ids = torch.argmax(logits, axis=-1)
            predicted_ids = torch.unique_consecutive(
                predicted_ids.T, dim=1).tolist()
            
        return predicted_ids
    
    def _decode_logits(self, predicted_ids: torch.Tensor) -> str:
        """Decodes logits to text"""
        transcriptions = []
        for ids in predicted_ids:
            transcription = self.token.string(ids)
            transcription = transcription.replace(
                " ", "").replace('|', " ").strip()
            transcriptions.append(transcription)
        return transcriptions