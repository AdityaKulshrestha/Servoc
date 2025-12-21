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