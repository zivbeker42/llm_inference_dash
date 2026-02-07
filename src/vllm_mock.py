from fastapi import FastAPI, Request, Response
from prometheus_client import generate_latest, Counter, Gauge, Histogram, CONTENT_TYPE_LATEST
import time
import random
import asyncio
import os
import yaml

app = FastAPI()

# --- Start of new/modified code ---

def load_config():
    config_path = 'config/latency_config.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except (IOError, yaml.YAMLError):
        return {
            'ttft': {'coefficient': 0.005, 'deviation_min': 0.01, 'deviation_max': 0.02},
            'itl': {'base_delay': 0.008, 'deviation_min': 0.0, 'deviation_max': 0.004}
        }

config = load_config()
ttft_config = config['ttft']
itl_config = config['itl']

# Prometheus Metrics
num_requests_running = Gauge('vllm_num_requests_running', 'Number of requests currently running')
num_requests_waiting = Gauge('vllm_num_requests_waiting', 'Number of requests waiting in queue')
prompt_tokens_total = Counter('vllm_prompt_tokens_total', 'Total number of prompt tokens processed')
generation_tokens_total = Counter('vllm_generation_tokens_total', 'Total number of generation tokens processed')
request_latency = Histogram('vllm_request_latency', 'Latency of vLLM requests', buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0])
ttft_latency = Histogram('vllm_ttft_seconds', 'Time to first token latency')
itl_latency = Histogram('vllm_time_per_output_token_seconds', 'Inter-token latency per output token')


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    num_requests_waiting.inc()
    num_requests_running.inc()
    start_time = time.time()
    try:
        request_data = await request.json()
        messages = request_data.get("messages", [])
        prompt = messages[0].get("content", "") if messages else ""
        prompt_tokens = len(prompt.split())

        # Simulate TTFT using config
        ttft_duration = (prompt_tokens * ttft_config['coefficient']) + random.uniform(ttft_config['deviation_min'], ttft_config['deviation_max'])
        await asyncio.sleep(ttft_duration)
        ttft_latency.observe(ttft_duration)

        # Simulate ITL using config
        generation_tokens = random.randint(5, 50)
        for _ in range(generation_tokens):
            itl_duration = itl_config['base_delay'] + random.uniform(itl_config['deviation_min'], itl_config['deviation_max'])
            await asyncio.sleep(itl_duration)
            itl_latency.observe(itl_duration)

        prompt_tokens_total.inc(prompt_tokens)
        generation_tokens_total.inc(generation_tokens)

        response_content = f"Simulated response for {prompt_tokens} prompt tokens and {generation_tokens} generation tokens."
        return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content,
                    },
                    "logprobs": None,
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": generation_tokens,
                "total_tokens": prompt_tokens + generation_tokens,
            },
        }
    finally:
        num_requests_running.dec()
        num_requests_waiting.dec()
        end_time = time.time()
        request_latency.observe(end_time - start_time)

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
