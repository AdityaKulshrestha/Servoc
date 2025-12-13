from locust import HttpUser, task

# locust -f test.py --headless -u 100 -r 5
class ASRBenchmarkUser(HttpUser):
    @task
    def test_asr_inference(self):
        audio_data = {
            "input_vector": [0.1, 0.2, 0.3, 0.4, 0.5]
            # "audio": "path/to/sample_audio.wav"
        }
        self.client.post("/v1/audio/transcription", json=audio_data)