#!/usr/bin/env bash

# Use libtcmalloc for better memory management
TCMALLOC="$(ldconfig -p | grep -Po "libtcmalloc.so.\d" | head -n 1)"
export LD_PRELOAD="${TCMALLOC}"

#
# SageAttention
#

# Extract compute capability safely.
GPU_ARCH=""

if command -v nvidia-smi >/dev/null 2>&1; then
    GPU_ARCH=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n 1 | grep -Eo '[0-9]+\.[0-9]+')
fi

echo "worker-comfyui: GPU: sm_${GPU_ARCH:-unknown}"

WHEEL_DIR="/opt/wheelhouse/${GPU_ARCH}"

if [ -n "$GPU_ARCH" ] && [ -d "$WHEEL_DIR" ]; then
    echo "Installing SageAttention for sm_${GPU_ARCH}..."
    
    # Install
    uv run python -m pip install --no-index --find-links=${WHEEL_DIR} sageattention
else
    # Fallback
    echo "worker-comfyui: SageAttention not found sm_${GPU_ARCH}! Installing fallback..."
    
    # Install
    uv run python -m pip install sageattention
fi

# Validate
uv run python -c "import importlib.metadata as m; import sageattention; print('SageAttention OK:', m.version('sageattention'))"

#
# Start
#

# Disable uv bytecode compilation at runtime to prevent 'Too many open files' (os error 24)
export UV_COMPILE_BYTECODE=0

RUNTIME_TARGET="${FRAMEPACK_RUNTIME_TARGET:-studio}"

case "${RUNTIME_TARGET}" in
    studio)
        START_CMD=(uv run studio.py)
        ;;
    serverless)
        START_CMD=(uv run serverless.py)
        ;;
    *)
        echo "Unknown FRAMEPACK_RUNTIME_TARGET='${RUNTIME_TARGET}', falling back to 'studio'."
        START_CMD=(uv run studio.py)
        ;;
esac

if [ -n "${FRAMEPACK_START_CMD:-}" ]; then
    echo "Starting FramePack with FRAMEPACK_START_CMD override: ${FRAMEPACK_START_CMD}"
    exec bash -lc "${FRAMEPACK_START_CMD}"
fi

echo "Starting FramePack target: ${RUNTIME_TARGET}"
exec "${START_CMD[@]}"