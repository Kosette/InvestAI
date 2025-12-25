#!/bin/bash
set -e

# 启动应用
echo "Starting mcp server ..."
exec uv run python server.py
