#!/usr/bin/env sh
set -eu

BASE_URL="${BASE_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-master1}"
PASSWORD="${PASSWORD:-master123}"
REQUEST_ID="${1:-1}"

COOKIE_JAR="$(mktemp)"
trap 'rm -f "$COOKIE_JAR" /tmp/race_1.txt /tmp/race_2.txt' EXIT

echo "1) GET /login to fetch csrf cookie"
curl -s -c "$COOKIE_JAR" "$BASE_URL/login/" > /dev/null
CSRF_TOKEN="$(awk '/csrftoken/ {print $7}' "$COOKIE_JAR" | tail -n 1)"

if [ -z "$CSRF_TOKEN" ]; then
  echo "Failed to read csrftoken cookie"
  exit 1
fi

echo "2) POST /login as $USERNAME"
curl -s -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  --data "username=$USERNAME&password=$PASSWORD&csrfmiddlewaretoken=$CSRF_TOKEN" > /dev/null

echo "3) Send two parallel take requests for request #$REQUEST_ID"
(
  CODE="$(curl -s -o /tmp/race_1.txt -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -X POST "$BASE_URL/master/requests/$REQUEST_ID/take/" \
    -H "X-CSRFToken: $CSRF_TOKEN" \
    --data "csrfmiddlewaretoken=$CSRF_TOKEN")"
  echo "$CODE" > /tmp/code1.txt
) &
PID1=$!
(
  CODE="$(curl -s -o /tmp/race_2.txt -w "%{http_code}" \
    -b "$COOKIE_JAR" \
    -X POST "$BASE_URL/master/requests/$REQUEST_ID/take/" \
    -H "X-CSRFToken: $CSRF_TOKEN" \
    --data "csrfmiddlewaretoken=$CSRF_TOKEN")"
  echo "$CODE" > /tmp/code2.txt
) &
PID2=$!

wait "$PID1"
wait "$PID2"

CODE1="$(cat /tmp/code1.txt)"
CODE2="$(cat /tmp/code2.txt)"

echo "Response codes: $CODE1 and $CODE2"
echo "Expected: one 302 (success redirect), one 409 (conflict)"
