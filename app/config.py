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
    model_path: Optional[str] = None
    device: str = "cpu"
    num_threads: int = 4


@dataclass
class ServerConfig:
    """Configuration for the server"""
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1

    batcher: BatcherConfig = BatcherConfig()
    engine: EngineConfig = EngineConfig() 

    # def __post_init__(self):
        # if self.engine.model_path is None:
            # raise ValueError("Model path must be specified in EngineConfig")  


config = ServerConfig()