import threading
import requests
import time
import random

BASE_URL = "http://localhost:5000"
ENDPOINTS = ["/", "/fail", "/slow", "/random"]
CONCURRENT_THREADS = 10
DELAY_BETWEEN_CALLS = 0.1  # seconds

def hit_endpoint():
    while True:
        endpoint = random.choice(ENDPOINTS)
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, timeout=10)
            print(f"[{endpoint}] {response.status_code}")
        except Exception as e:
            print(f"[{endpoint}] Error: {e}")
        time.sleep(DELAY_BETWEEN_CALLS)

def main():
    threads = []
    for _ in range(CONCURRENT_THREADS):
        t = threading.Thread(target=hit_endpoint, daemon=True)
        t.start()
        threads.append(t)
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
