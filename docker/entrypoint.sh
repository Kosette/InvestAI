#!/bin/bash
set -e

# 启动应用
echo "Starting application..."
exec uv run python run_monitor.py
