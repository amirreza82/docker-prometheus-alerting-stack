import requests
import time
import math
from itertools import cycle

# تنظیمات
BASE_RATE = 50          # حداقل تعداد درخواست‌ها در هر ثانیه
AMPLITUDE = 30          # دامنه تغییرات
PERIOD = 120            # دوره سینوسی بر حسب ثانیه

ENDPOINTS = [
    "http://localhost:5050/",
    "http://localhost:5050/fail",
    "http://localhost:5050/slow",
    "http://localhost:5050/random"
]

def get_current_rate(t):
    # نرخ درخواست لحظه‌ای به صورت سینوسی (بین BASE_RATE - AMPLITUDE تا BASE_RATE + AMPLITUDE)
    return BASE_RATE + AMPLITUDE * math.sin(2 * math.pi * t / PERIOD)

def main():
    start_time = time.time()
    endpoints_cycle = cycle(ENDPOINTS)
    while True:
        elapsed = time.time() - start_time
        current_rate = get_current_rate(elapsed)
        current_rate = max(1, current_rate)  # جلوگیری از منفی شدن نرخ

        # محاسبه تعداد درخواست در این ثانیه
        requests_this_second = int(current_rate)
        interval = 1.0 / requests_this_second

        for _ in range(requests_this_second):
            endpoint = next(endpoints_cycle)
            try:
                requests.get(endpoint, timeout=2)
            except Exception as e:
                print(f"Error requesting {endpoint}: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    main()
