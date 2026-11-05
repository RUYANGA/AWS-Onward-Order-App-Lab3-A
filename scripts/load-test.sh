#!/usr/bin/env bash
# Drives CPU load through the public ALB so you can watch the service scale out.
# Usage: ./scripts/load-test.sh http://<alb-dns-name> [minutes]
# Needs "hey" (https://github.com/rakyll/hey): brew install hey / go install github.com/rakyll/hey@latest
set -euo pipefail
URL=${1:?ALB URL required}; MINUTES=${2:-8}
echo "Sending load to $URL for $MINUTES minutes. Watch: ECS > service > Tasks, and the CPU alarm in CloudWatch."
hey -z "${MINUTES}m" -c 150 -m POST -T application/json \
  -d '{"merchant":"Load Test","customer":"Bot","zone":"national","service":"express","weight_kg":4}' \
  "$URL/api/orders"
