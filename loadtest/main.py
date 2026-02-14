import asyncio
import click
import httpx
import time
import random
from tqdm import tqdm

DEFAULT_URL = "http://localhost:8080/v1/chat/completions"
DEFAULT_API_KEY = "super-secret-key"

TENANTS = [
    {"org_unit": "finance", "team": "fraud-detection", "app_id": "fraud-model-v1"},
    {"org_unit": "finance", "team": "accounting", "app_id": "invoice-parser"},
    {"org_unit": "marketing", "team": "content-generation", "app_id": "blog-writer"},
    {"org_unit": "marketing", "team": "seo", "app_id": "keyword-analyzer"},
    {"org_unit": "engineering", "team": "infra", "app_id": "ci-optimizer"},
    {"org_unit": "engineering", "team": "backend", "app_id": "code-generator"},
]

MODELS = ["gpt-4", "gpt-3.5-turbo", "claude-2", "mistral-7b"]

async def send_request(client, url, headers, payload):
    try:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.status_code
    except httpx.HTTPStatusError as e:
        return e.response.status_code
    except httpx.RequestError:
        return -1

@click.group()
def cli():
    pass

@cli.command()
@click.option("--url", default=DEFAULT_URL, help="Gateway URL.")
@click.option("--api-key", default=DEFAULT_API_KEY, help="Gateway API Key.")
@click.option("--rate", default=10, help="Requests per second.")
@click.option("--duration", default=60, help="Duration in seconds.")
def steady(url, api_key, rate, duration):
    """Run a steady load test from a single tenant."""
    click.echo(f"Running steady load test at {rate} rps for {duration}s")

    tenant = TENANTS[0]
    headers = {
        "X-API-Key": api_key,
        "X-Org-Unit": tenant["org_unit"],
        "X-Team": tenant["team"],
        "X-App-Id": tenant["app_id"],
    }
    payload = {
        "model": random.choice(MODELS),
        "messages": [{"role": "user", "content": "Hello!"}],
    }

    async def main():
        async with httpx.AsyncClient() as client:
            tasks = []
            start_time = time.time()
            with tqdm(total=rate * duration) as pbar:
                while time.time() - start_time < duration:
                    for _ in range(rate):
                        tasks.append(send_request(client, url, headers, payload))

                    if tasks:
                        results = await asyncio.gather(*tasks)
                        pbar.update(len(results))
                        tasks = []

                    await asyncio.sleep(1)

    asyncio.run(main())
    click.echo("Load test finished.")


@cli.command()
@click.option("--url", default=DEFAULT_URL, help="Gateway URL.")
@click.option("--api-key", default=DEFAULT_API_KEY, help="Gateway API Key.")
@click.option("--requests", default=100, help="Total number of requests.")
def burst(url, api_key, requests):
    """Run a burst load test."""
    click.echo(f"Running burst load test with {requests} requests")

    tenant = TENANTS[0]
    headers = {
        "X-API-Key": api_key,
        "X-Org-Unit": tenant["org_unit"],
        "X-Team": tenant["team"],
        "X-App-Id": tenant["app_id"],
    }
    payload = {
        "model": random.choice(MODELS),
        "messages": [{"role": "user", "content": "Hello!"}],
    }

    async def main():
        async with httpx.AsyncClient() as client:
            tasks = [send_request(client, url, headers, payload) for _ in range(requests)]
            results = []
            with tqdm(total=requests) as pbar:
                for f in asyncio.as_completed(tasks):
                    result = await f
                    results.append(result)
                    pbar.update(1)

    asyncio.run(main())
    click.echo("Burst load test finished.")


@cli.command()
@click.option("--url", default=DEFAULT_URL, help="Gateway URL.")
@click.option("--api-key", default=DEFAULT_API_KEY, help="Gateway API Key.")
@click.option("--rate", default=20, help="Total requests per second.")
@click.option("--duration", default=60, help="Duration in seconds.")
def multi_tenant(url, api_key, rate, duration):
    """Run a load test simulating multiple tenants."""
    click.echo(f"Running multi-tenant load test at {rate} rps for {duration}s")

    async def main():
        async with httpx.AsyncClient() as client:
            tasks = []
            start_time = time.time()
            with tqdm(total=rate * duration) as pbar:
                while time.time() - start_time < duration:
                    for _ in range(rate):
                        tenant = random.choice(TENANTS)
                        headers = {
                            "X-API-Key": api_key,
                            "X-Org-Unit": tenant["org_unit"],
                            "X-Team": tenant["team"],
                            "X-App-Id": tenant["app_id"],
                        }
                        payload = {
                            "model": random.choice(MODELS),
                            "messages": [{"role": "user", "content": "Hello!"}],
                        }
                        tasks.append(send_request(client, url, headers, payload))

                    if tasks:
                        results = await asyncio.gather(*tasks)
                        pbar.update(len(results))
                        tasks = []

                    await asyncio.sleep(1)

    asyncio.run(main())
    click.echo("Multi-tenant load test finished.")


if __name__ == "__main__":
    cli()
