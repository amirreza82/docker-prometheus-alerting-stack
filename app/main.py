from flask import Flask
from prometheus_client import start_http_server, Summary, Counter, Gauge
import random
import time

app = Flask(__name__)

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests')
TEMPERATURE = Gauge('app_temperature_celsius', 'Simulated temperature')

@app.route("/")
@REQUEST_TIME.time()
def index():
    time.sleep(0.6)
    REQUEST_COUNT.inc()
    temp = random.uniform(30, 100)
    TEMPERATURE.set(temp)
    return f"Hello! Current temperature: {temp:.2f}°C\n"

if __name__ == "__main__":
    start_http_server(8000)
    app.run(host="0.0.0.0", port=5000)