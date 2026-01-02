#!/bin/bash

echo "Starting HA Agent..."
uv run python deployment/controller/daemon.py &

echo "Started Servoc Inference Engine Server"
exec uv run python main.py