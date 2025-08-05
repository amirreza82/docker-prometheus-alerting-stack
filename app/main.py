from flask import Flask, Response, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import random
import threading
from functools import wraps


app = Flask(__name__)

# ======= METRICS ========
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("request_processing_seconds", "Request latency", ["endpoint"])
IN_PROGRESS = Gauge("in_progress_requests", "Requests currently being processed")
SUCCESS_COUNT = Counter("http_success_total", "Total successful requests (2xx)")
CLIENT_ERROR_COUNT = Counter("http_4xx_errors_total", "Total client errors (4xx)")
SERVER_ERROR_COUNT = Counter("http_5xx_errors_total", "Total server errors (5xx)")
USER_REQUESTS = Counter("user_requests_total", "Requests per user", ["ip"])
ENDPOINT_HITS = Counter("endpoint_hits_total", "Hits per endpoint", ["endpoint"])

# ======= METRIC WRAPPER ========
def track_metrics(endpoint):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            IN_PROGRESS.inc()
            start = time.time()
            ip = request.remote_addr

            try:
                response = func(*args, **kwargs)
                duration = time.time() - start

                status_code = 200
                if isinstance(response, tuple):
                    status_code = response[1]

                REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
                REQUEST_COUNT.labels(method="GET", endpoint=endpoint, status=status_code).inc()
                ENDPOINT_HITS.labels(endpoint=endpoint).inc()
                USER_REQUESTS.labels(ip=ip).inc()

                if 200 <= status_code < 300:
                    SUCCESS_COUNT.inc()
                elif 400 <= status_code < 500:
                    CLIENT_ERROR_COUNT.inc()
                elif 500 <= status_code < 600:
                    SERVER_ERROR_COUNT.inc()

                return response
            finally:
                IN_PROGRESS.dec()
        return wrapped
    return wrapper

# ========== ROUTES ==========

@app.route("/")
@track_metrics("/")
def index():
    time.sleep(random.uniform(0.05, 0.2))  # کمتر ولی سریع‌تر
    return "Hello, world!"

@app.route("/fail")
@track_metrics("/fail")
def fail():
    time.sleep(random.uniform(0.01, 0.1))
    return "Internal Server Error", 500

@app.route("/slow")
@track_metrics("/slow")
def slow():
    time.sleep(random.uniform(3, 7))  # کمی طولانی‌تر
    return "Very slow response!"

@app.route("/random")
@track_metrics("/random")
def random_response():
    status = random.choices(
        [200, 400, 404, 500, 503],
        weights=[70, 10, 5, 10, 5],
        k=1
    )[0]
    time.sleep(random.uniform(0.05, 0.2))
    if status == 200:
        return "Random OK"
    elif status == 400:
        return "Bad Request", 400
    elif status == 404:
        return "Not Found", 404
    elif status == 500:
        return "Server Error", 500
    return "Service Unavailable", 503

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

# ====== Background Load Generator =======
def generate_load():
    import requests
    endpoints = ["http://localhost:5000/", "http://localhost:5000/slow", "http://localhost:5000/random", "http://localhost:5000/fail"]
    while True:
        url = random.choice(endpoints)
        try:
            requests.get(url, timeout=5)
        except Exception:
            pass
        time.sleep(0.05)  # ارسال تقریبا 20 درخواست در ثانیه

if __name__ == "__main__":
    import threading
    thread = threading.Thread(target=generate_load, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=5000)
