# LLM Inference PaaS Observability

This project provides a comprehensive, local-first environment for monitoring a vLLM-based inference server. It includes a metrics gateway, a load generator, and a pre-configured Prometheus and Grafana stack with detailed, stakeholder-specific dashboards.

## Project Structure

```
.
├── config/
│   ├── baselines.yaml
│   └── quotas.yaml
├── gateway/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── loadtest/
│   ├── main.py
│   └── requirements.txt
├── observability/
│   ├── docker-compose.yml
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── 1_org_leaders_dashboard.json
│   │   │   ├── 2_infra_leaders_dashboard.json
│   │   │   ├── 3_devops_oncall_dashboard.json
│   │   │   └── 4_customer_dashboard.json
│   │   └── provisioning/
│   │       ├── dashboards.yml
│   │       └── datasources.yml
│   └── prometheus/
│       └── prometheus.yml
├── src/
│   └── vllm_mock.py
├── Dockerfile
├── README.md
└── requirements.txt
```

## Setup and Running

1.  **Build and run the Docker containers:**

    Navigate to the project root directory and run:
    ```bash
    docker compose -f observability/docker-compose.yml up --build -d
    ```

    This will start the `vllm-mock-server`, `gateway`, `prometheus`, and `grafana` services.

2.  **Access the services:**

    *   **vLLM Mock Server:** http://localhost:8000
    *   **Metrics Gateway:** http://localhost:8080
    *   **Prometheus:** http://localhost:9090
    *   **Grafana:** http://localhost:3000 (user: `admin`, password: `admin`)

    Four Grafana dashboards are automatically provisioned:
    - Organization Leaders Dashboard
    - Infrastructure Leaders Dashboard
    - DevOps On-call Dashboard
    - Customer Dashboard

## Running the Load Tester

The load tester simulates realistic traffic to the metrics gateway.

1.  **Install dependencies:**

    ```bash
    pip install -r loadtest/requirements.txt
    ```

2.  **Run a load scenario:**

    The load tester is a CLI with three subcommands: `steady`, `burst`, and `multi-tenant`.

    *   **Steady load from a single tenant:**
        ```bash
        python loadtest/main.py steady --rate 10 --duration 60
        ```

    *   **Burst of requests:**
        ```bash
        python loadtest/main.py burst --requests 200
        ```

    *   **Load from multiple tenants:**
        ```bash
        python loadtest/main.py multi-tenant --rate 20 --duration 120
        ```

    Use `--help` for more options, e.g., `python loadtest/main.py steady --help`.

## Running Tests

The original tests verify the vLLM mock server's metrics.

1.  **Ensure services are running.**

2.  **Install test dependencies:**

    ```bash
    pip install pytest httpx
    ```

3.  **Run tests:**

    ```bash
    pytest tests/test_mock.py
    ```
