#!/bin/bash
set -e

# 启动应用
echo "Starting monitor ..."
exec uv run python run_monitor.py
