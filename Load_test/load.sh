#!/bin/bash

ENDPOINTS=(
  "http://localhost:5050/"
  "http://localhost:5050/user"
  "http://localhost:5050/data"
  "http://localhost:5050/fail"
)

DURATION_SECONDS=300

echo "Starting dynamic load simulation..."

for ((t=0; t<$DURATION_SECONDS; t++)); do
  # 🔁 هر بار فایل پیکربندی رو بخونه
  source config.env

  RATE=$(echo "$BASE_RATE + $AMPLITUDE * s(2 * 3.14159 * $t / $PERIOD)" | bc -l)
  RATE=${RATE%.*}
  [ "$RATE" -lt 1 ] && RATE=1

  URL=${ENDPOINTS[$RANDOM % ${#ENDPOINTS[@]}]}

  echo "[$(date +%T)] Sending $RATE RPS to $URL"

  hey -z 1s -q $RATE -c 10 "$URL" &

  sleep 1
done

wait
echo "Done."
