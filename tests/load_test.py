import httpx
import asyncio
import time
import yaml
import os
import numpy as np
from faker import Faker

def load_config(config_file_path: str) -> dict:
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")
    with open(config_file_path, 'r') as file:
        return yaml.safe_load(file)

fake = Faker()

def generate_random_message(min_words: int, max_words: int) -> str:
    num_words = np.random.randint(min_words, max_words + 1)
    return ' '.join(fake.words(num_words)).capitalize() + "."

async def send_request(client, url, message):
    chat_payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}]
    }
    try:
        print(f"Sending request with {len(message.split())} words...")
        response = await client.post(url, json=chat_payload, timeout=60.0)
        response.raise_for_status()
        print("Received response.")
    except httpx.RequestError as e:
        print(f"An error occurred while sending the request: {e}")

async def main():
    config = load_config('config/load_test_config.yaml')
    server_config = config['server']
    load_test_config = config['load_test']
    message_config = config['message_content']

    url = f"{server_config['base_url']}{server_config['chat_completions_endpoint']}"

    mean_inter_arrival_time = 1.0 / load_test_config['target_arrival_rate_per_second']

    print("Starting load test...")
    start_time = time.time()

    async with httpx.AsyncClient() as client:
        tasks = []
        while (time.time() - start_time) < load_test_config['duration_seconds']:
            inter_arrival_time = np.random.exponential(scale=mean_inter_arrival_time)
            await asyncio.sleep(inter_arrival_time)

            message = generate_random_message(message_config['min_words'], message_config['max_words'])
            task = asyncio.create_task(send_request(client, url, message))
            tasks.append(task)

        await asyncio.gather(*tasks)
    print("Load test finished.")

if __name__ == "__main__":
    asyncio.run(main())
