# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## High-level code architecture and structure

This project provides a local environment to mock LLM inference, collect metrics using Prometheus, and visualize them with Grafana.

The main components are:
- **`src/vllm_mock.py`**: A FastAPI application that serves an OpenAI-compatible endpoint for chat completions at `/v1/chat/completions`. It also exposes Prometheus metrics at `/metrics`. The metrics include counters for tokens, gauges for running and waiting requests, and a histogram for request latency.
- **`deploy/`**: Contains the `docker-compose.yml` file to orchestrate the services.
  - **`prometheus/`**: Configuration for Prometheus to scrape the metrics from the mock server.
  - **`grafana/`**: Provisioning and dashboard configuration for Grafana. The dashboard `llm-metrics-dashboard.json` is set up to visualize the metrics from Prometheus.
- **`tests/test_mock.py`**: Pytest tests that send requests to the mock server and verify that the Prometheus metrics are updated correctly.

The overall workflow is:
1. The `docker-compose.yml` starts the `vllm-mock-server`, `prometheus`, and `grafana` services.
2. The `prometheus` service is configured to scrape the `/metrics` endpoint of the `vllm-mock-server`.
3. The `grafana` service is provisioned with a datasource connected to Prometheus and a dashboard to visualize the LLM metrics.

## Common Commands

- **Build and run all services (mock server, Prometheus, Grafana)**:
  ```bash
  docker-compose -f deploy/docker-compose.yml up --build -d
  ```

- **Install test dependencies**:
  ```bash
  pip install pytest httpx
  ```

- **Run tests**:
  The tests assume that the services are already running.
  ```bash
  pytest tests/test_mock.py
  ```
