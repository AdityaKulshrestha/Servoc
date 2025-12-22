# Servoc
A simple engine for serving Voice models on CPUs.

## Run 
1. Install the dependencies
    ```bash
    uv sync
    ```
2. Activate the virtual environment
    ```bash
    source .venv/bin/activate
    ```
3. Run the application
    ```bash
    python main.py
    ```


## Benchmark
To run the benchmark tests, execute the following command:
1. Enter the respective directory
    ```bash
    cd benchmarks/asr
    ```

2. Run the load script
    ```bash
    locust -f ./test.py --headless -u 20 -r 5 -H http://localhost:8080
    ```

## Docker Deployment
To deploy the application using Docker, follow these steps:
1. Build the Docker image
    ```bash
    docker build -t servoc:latest .
    ```
2. Run the Docker container
    ```bash
    docker run -d -p 8080:8080 --cpuset-cpus="0-31" --cpuset-mems="0" --privileged --name servoc_container servoc:latest
    ```

## TODOs
- [x] Add Whisper model support
    - [x] Add support for sending audios using openai client
    - [x] Change response schema to openai
    - [x] Add functionality to convert the audio bytes to numpy/tensor.
    - [x] Add True batching in whisper model inference
- [x] Test the initial whisper model support
- [x] Add Dockerfile for containerized deployments with CPU core pinning and NUMA awareness
- [ ] Add ~~nginx~~HAProxy for load balancing based on custom logic of core utilization
- [ ] Add IndicParler TTS
- [ ] Evaluate the performance on IndicParler TTS
- [ ] Add script for automated deployments using core load and stress testing
- [ ] Add Kubernetes manifests for orchestrated deployments with resource management
- [ ] Add monitoring using Prometheus and Grafana for real-time performance tracking