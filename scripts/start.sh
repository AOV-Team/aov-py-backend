#!/usr/bin/env bash
echo "Starting all processes"
echo "Must have virtual environment enabled"
echo "FOR TESTING ONLY"
echo
../../redis-3.0.7/src/redis-server &
echo
flower -A backend.settings -p 5555 &
echo
celery -A backend.settings worker -l info &
