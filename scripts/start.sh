#!/usr/bin/env bash
echo "Starting all processes"
echo "Must have virtual environment enabled"
echo "FOR TESTING ONLY"
echo
flower -A backend.settings -p 5555 -conf=flowerconfig.py &
echo
celery -A backend.settings worker -B -l info &
