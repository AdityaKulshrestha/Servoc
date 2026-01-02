from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BatcherConfig:
    """Configuration for the batcher system"""
    max_batch_size: int = 8
    max_wait_time_ms: int = 100
    queue_size: int = 1024


@dataclass
class EngineConfig:
    """Configuration for the inference engine"""
    # model_path: Optional[str] = "openai/whisper-large-v3"
    # model_type: str = "whisper"
    model_path: Optional[str] = "asr_models/hindi.pt"
    model_type: str = "wav2vec2"
    device: str = "cpu"
    language: str = "hindi"
    num_threads: int = 4
    dtype: int = "bfloat16"


@dataclass
class ServerConfig:
    """Configuration for the server"""
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1

    batcher: BatcherConfig = BatcherConfig()
    engine: EngineConfig = EngineConfig() 



config = ServerConfig()