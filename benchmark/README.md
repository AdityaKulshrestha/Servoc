# Benchmark


## Instructions
To run the benchmark tests, execute the following command:
1. Enter the respective directory
    ```bash
    cd benchmarks/asr
    ```

2. Run the load script
    ```bash
    locust -f ./test.py --headless -u 20 -r 5 -H http://localhost:8080
    ```

## Sample curl request

```
curl http://localhost:8080/v1/audio/transcriptions \
  -H "Authorization: Bearer None" \
  -H "Content-Type: multipart/form-data" \
  -F file="@/path/to/file/audio.mp3" \
  -F model="wav2vec"
```