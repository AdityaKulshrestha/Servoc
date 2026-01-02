from abc import ABC, abstractmethod
from typing import Any, Dict


class STTEngine(ABC):
    def __init__(self):
        self.device = "cpu"
        self.model = None
        self.processor = None
        self.tokenizer = None
        self._is_loaded = False


    @abstractmethod
    def transcribe(self, audio: Any, params: Dict[str, Any]) -> str:
        """
        Transcribe the given audio input.

        Args:
            audio: The audio input to transcribe.
            params: Additional parameters for transcription.

        Returns:
            The transcribed text.
        """
        pass


class TTSEngine(ABC):
    
    @abstractmethod
    def synthesize(self, text: str, params: Dict[str, Any]) -> Any:
        """
        Synthesize speech from the given text input.

        Args:
            text: The text input to synthesize.
            params: Additional parameters for synthesis.

        Returns:
            The synthesized audio output.
        """
        pass