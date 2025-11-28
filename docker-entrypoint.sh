#!/bin/sh
set -e

mkdir -p ./media/chat/images

# Use uvloop + httptools
export UVICORN_LOOP=uvloop
export UVICORN_HTTP=httptools

uv run uvicorn main:app \
    --workers 4 \
    --host 0.0.0.0 \
    --port 8000 \
    --http httptools \
    --loop uvloop

