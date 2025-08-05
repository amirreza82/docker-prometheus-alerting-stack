#!/bin/bash

ENDPOINTS=(
  "http://localhost:5050/"
  "http://localhost:5050/fail"
  "http://localhost:5050/slow"
  "http://localhost:5050/random"
)

CONFIG_FILE="config.env"

load_config() {
  if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
  else
    BASE_RATE=50
    AMPLITUDE=20
    PERIOD=5
  fi
}

load_config

LAST_MOD_TIME=0
SECONDS_PASSED=0

echo "🚀 Starting load generator with dynamic config from $CONFIG_FILE"

while true; do
  CURRENT_MOD_TIME=$(stat -c %Y "$CONFIG_FILE" 2>/dev/null || echo 0)
  if [ "$CURRENT_MOD_TIME" -ne "$LAST_MOD_TIME" ]; then
    echo "⚙️ Reloading config at $(date +%T)"
    load_config
    LAST_MOD_TIME=$CURRENT_MOD_TIME
  fi


  RATE_FLOAT=$(awk -v base=$BASE_RATE -v amp=$AMPLITUDE -v period=$PERIOD -v t=$SECONDS_PASSED 'BEGIN {
    pi = 3.14159265359;
    val = base + amp * sin(2 * pi * t / period);
    if(val < 1) val = 1;  # حداقل 1 درخواست
    printf("%.0f", val);
  }')

  URL=${ENDPOINTS[$RANDOM % ${#ENDPOINTS[@]}]}

  echo "[$(date +%T)] Sending $RATE_FLOAT requests to $URL"

  hey -z 1s -q $RATE_FLOAT -c 10 "$URL" > /dev/null 2>&1 || echo "❌ hey failed"

  sleep 1
  SECONDS_PASSED=$((SECONDS_PASSED+1))
done
