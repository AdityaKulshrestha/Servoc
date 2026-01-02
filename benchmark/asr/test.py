import os
import time
from openai import OpenAI
from locust import HttpUser, task, TaskSet, task, between, events

# locust -f test.py --headless -u 2 -r 1
# locust -f test.py --headless -u 50 -r 5 -H http://localhost:8080 --run-time 5m --csv=benchmark
class ASRBenchmarkTask(TaskSet):
    """
    STT benchmarking tasks using OpenAI client.
    The synchronous OpenAI client works with Locust because gevent 
    patches HTTP calls automatically.
    """
    @task
    def transcribe_audio(self):
        """Test audio file transcription"""
        start_time = time.time()
        try:
            with open(self.user.audio_files[0], "rb") as f:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="json"
                )
            
            # Calculate latency
            latency = (time.time() - start_time) * 1000
            # Validate response (e.g. check transcription length)
            if not response.text or not response.text.strip():
                raise ValueError("Empty transcription result")
            
            # Fire success event with custom metrics
            events.request.fire(
                request_type="audio_transcription",
                name="transcribe_audio",
                response_time=latency,
                response_length=len(response.text),
                exception=None,
                context=self.user.context()
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            events.request.fire(
                request_type="audio_transcription",
                name="transcribe_audio",
                response_time=latency,
                response_length=0,
                exception=e,
                context=self.user.context()
            )


class ASRUser(HttpUser):
    """
    User class for STT Benchmarking
    """
    tasks = [ASRBenchmarkTask]
    host = os.getenv("STT_API_HOST", "http://localhost:8080")
    # wait_time = between(1, 3)

    def on_start(self):
        self.client = OpenAI(
            base_url=os.getenv("STT_OPENAI_BASE_URL", "http://localhost:8080/v1"),
            api_key=os.getenv("STT_OPENAI_API_KEY", "test")
        )
        self.audio_files = ["./sample_audios/audio.wav"]

    
    def on_stop(self):
        pass