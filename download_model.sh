#!/bin/bash
set -e

MODEL_DIR="./models"
MODEL_FILE="Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/${MODEL_FILE}"

mkdir -p "$MODEL_DIR"

if [ -f "${MODEL_DIR}/${MODEL_FILE}" ]; then
    echo "Model already downloaded: ${MODEL_DIR}/${MODEL_FILE}"
    exit 0
fi

echo "Downloading Qwen2.5-0.5B-Instruct (Q4_K_M, ~400MB)..."
curl -L --progress-bar -o "${MODEL_DIR}/${MODEL_FILE}" "$MODEL_URL"
echo "Done: ${MODEL_DIR}/${MODEL_FILE}"
