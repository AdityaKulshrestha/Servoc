from locust import HttpUser, task


class ASRBenchmarkUser(HttpUser):
    @task
    def test_asr_inference(self):
        audio_data = {
            "audio": "path/to/sample_audio.wav"
        }
        self.client.post("/asr/infer", json=audio_data)