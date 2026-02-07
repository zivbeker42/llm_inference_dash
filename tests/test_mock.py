import httpx
import pytest
import time

MOCK_SERVER_URL = "http://localhost:8000"

def get_metric_value(metrics_content: str, metric_name: str):
    for line in metrics_content.split('\n'):
        if line.startswith(metric_name):
            return float(line.split()[-1])
    return None

@pytest.fixture(scope="module")
def setup_mock_server():
    # In a real scenario, you'd start your docker-compose environment here
    # For this test, we assume the docker-compose environment is already running
    # Or, you could use `pytest-docker` or similar fixtures.
    print("\nAssuming docker-compose services (vllm-mock-server, prometheus, grafana) are running.")
    print("Please ensure you run `docker-compose up --build -d` in the deploy directory before running tests.")
    time.sleep(5)  # Give the server some time to start
    yield
    # Teardown (if you started services in the fixture)

def test_chat_completions_and_metrics(setup_mock_server):
    # 1. Get initial metrics
    initial_metrics_res = httpx.get(f"{MOCK_SERVER_URL}/metrics")
    initial_metrics_res.raise_for_status()
    initial_metrics = initial_metrics_res.text

    initial_prompt_tokens = get_metric_value(initial_metrics, "vllm_prompt_tokens_total_total")
    initial_generation_tokens = get_metric_value(initial_metrics, "vllm_generation_tokens_total_total")
    initial_requests_running = get_metric_value(initial_metrics, "vllm_num_requests_running")
    initial_requests_waiting = get_metric_value(initial_metrics, "vllm_num_requests_waiting")

    assert initial_requests_running is not None
    assert initial_requests_waiting is not None

    # 2. Send a request to the chat completions endpoint
    chat_payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}]
    }
    chat_res = httpx.post(f"{MOCK_SERVER_URL}/v1/chat/completions", json=chat_payload)
    chat_res.raise_for_status()
    chat_response = chat_res.json()

    assert "choices" in chat_response
    assert len(chat_response["choices"]) > 0
    assert "content" in chat_response["choices"][0]["message"]

    # 3. Get updated metrics and verify
    updated_metrics_res = httpx.get(f"{MOCK_SERVER_URL}/metrics")
    updated_metrics_res.raise_for_status()
    updated_metrics = updated_metrics_res.text

    updated_prompt_tokens = get_metric_value(updated_metrics, "vllm_prompt_tokens_total_total")
    updated_generation_tokens = get_metric_value(updated_metrics, "vllm_generation_tokens_total_total")
    updated_requests_running = get_metric_value(updated_metrics, "vllm_num_requests_running")
    updated_requests_waiting = get_metric_value(updated_metrics, "vllm_num_requests_waiting")

    assert updated_prompt_tokens > initial_prompt_tokens
    assert updated_generation_tokens > initial_generation_tokens
    assert updated_requests_running == 0.0  # Should be 0 after request completes
    assert updated_requests_waiting == 0.0  # Should be 0 after request completes

    # Verify latency metric exists (its value is non-deterministic)
    latency_metric_line = next((line for line in updated_metrics.split('\n') if line.startswith('# HELP vllm_request_latency')), None)
    assert latency_metric_line is not None
