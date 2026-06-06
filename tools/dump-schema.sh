#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="$(dirname "$0")/../docker-compose.dev.yml"
OUTPUT="${1:-schema.sql}"

docker compose -f "$COMPOSE_FILE" exec -T postgres \
  pg_dump \
    --username=academika \
    --dbname=academika \
    --schema-only \
    --no-owner \
    --no-acl \
  > "$OUTPUT"

echo "Schema dumped to $OUTPUT"
