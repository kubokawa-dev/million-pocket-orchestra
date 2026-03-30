#!/usr/bin/env bash
# Rebase onto latest origin/main and push; retry when another workflow wins the race.
set -euo pipefail

BRANCH="${1:-main}"
MAX_ATTEMPTS="${GIT_PUSH_MAX_ATTEMPTS:-10}"

for i in $(seq 1 "$MAX_ATTEMPTS"); do
  git pull origin "$BRANCH" --rebase
  if git push origin "$BRANCH"; then
    exit 0
  fi
  if [ "$i" -eq "$MAX_ATTEMPTS" ]; then
    echo "❌ git push failed after $MAX_ATTEMPTS attempts"
    exit 1
  fi
  echo "⚠️ Push rejected (remote advanced); retry $i/$MAX_ATTEMPTS..."
  sleep $((2 + RANDOM % 8))
done
