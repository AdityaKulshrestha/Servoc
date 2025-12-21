import io
import numpy as np
import librosa
import soundfile as sf
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class AudioSample:
    """Decoded audio sample ready for processing."""
    audio: np.ndarray           # PCM samples as float32
    sample_rate: int            # Original sample rate
    duration: float             # Duration in seconds
    original_format: str        # mp3, wav, etc


async def decode_audio(
    file_bytes: bytes,
    target_sample_rate: int = 16000,
) -> AudioSample:
    """
    Decode audio bytes to numpy array with resampling
    
    Supports: MP3, WAV, FLAC, OGG, M4A
    """
    buffer = io.BytesIO(file_bytes)
    audio, sr = sf.read(buffer, dtype='float32')

    # Convert stereo to mono
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    # Resample if needed
    if sr != target_sample_rate:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sample_rate)
        sr = target_sample_rate
    
    return AudioSample(
        audio=audio,
        sample_rate=sr,
        duration=len(audio) / sr,
        original_format='unknown'  # Could be improved by detecting format
    )

    