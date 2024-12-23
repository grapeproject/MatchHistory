#!/bin/bash
export PYTHONPATH="$(pwd)/backend"
uvicorn lol.asgi:app --reload
