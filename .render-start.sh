#!/usr/bin/env bash
set -euo pipefail

if [ -n "${KEYS_ENV:-}" ]; then
  printf '%s' "$KEYS_ENV" > keys.env
fi

if [ -n "${TOKEN_JSON:-}" ]; then
  printf '%s' "$TOKEN_JSON" > token.json
fi

if [ -n "${CLIENT_SECRET_JSON:-}" ]; then
  printf '%s' "$CLIENT_SECRET_JSON" > client_secret.json
fi

python bot.py
