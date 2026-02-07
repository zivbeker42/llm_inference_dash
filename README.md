# LLM Inference Dashboard

This project provides a local-first environment to mock LLM inference, collect metrics using Prometheus, and visualize them with Grafana.

## Project Structure

```
llm_inference_dash/
├── src/
│   └── vllm_mock.py
├── deploy/
│   ├── docker-compose.yml
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   └── llm-metrics-dashboard.json
│   │   └── provisioning/
│   │       ├── datasources/
│   │       │   └── datasource.yml
│   │       └── dashboards/
│   │           └── dashboard.yml
├── tests/
│   └── test_mock.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Setup and Running

1.  **Build and run the Docker containers:**

    Navigate to the project root directory and run:
    ```bash
    docker-compose -f deploy/docker-compose.yml up --build -d
    ```

    This will start the `vllm-mock-server`, `prometheus`, and `grafana` services.

2.  **Access the services:**

    *   **vLLM Mock Server:** http://localhost:8000
        *   OpenAI-compatible completions endpoint: `http://localhost:8000/v1/chat/completions`
        *   Prometheus metrics endpoint: `http://localhost:8000/metrics`
    *   **Prometheus:** http://localhost:9090
    *   **Grafana:** http://localhost:3000 (default user: `admin`, password: `admin`)

    The Grafana dashboard "LLM Metrics Dashboard" should be automatically provisioned.

## Running Tests

1.  **Ensure services are running:** Make sure you have started the Docker containers as described in the "Setup and Running" section.

2.  **Install test dependencies:**

    ```bash
    pip install pytest httpx
    ```

3.  **Run tests:**

    ```bash
    pytest tests/test_mock.py
    ```

    The tests will send requests to the mock server and verify that Prometheus metrics are correctly incremented.
