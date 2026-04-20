#
# Base
#
FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04 AS base
ENV DEBIAN_FRONTEND=noninteractive

ENV UV_CACHE_DIR=/var/cache/uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_FROZEN=1
ENV UV_NO_EDITABLE=1

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

# Install Python
RUN --mount=type=cache,target=/var/cache/uv,id=uv-cache,sharing=locked \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
        uv python install

# Install base dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Project directory
WORKDIR /app

#
# Builder
#
FROM base AS builder

# Install dependencies
RUN --mount=type=cache,target=/var/cache/uv,id=uv-cache,sharing=locked \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
        uv venv --relocatable && \
        uv sync --extra runpod --no-install-project --no-dev

# Use the virtual environment for all subsequent commands
ENV PATH="/app/.venv/bin:$PATH"

#
# SageAttention 2 Builder
#
FROM builder AS sageattention_builder

ARG SAGEATTENTION_REF="d1a57a546c3d395b1ffcbeecc66d81db76f3b4b5"

# SageAttention build tuning (optimized defaults for 8 cores / 32 GB RAM)
ARG EXT_PARALLEL="4"
ARG MAX_JOBS="4"
ARG CMAKE_BUILD_PARALLEL_LEVEL="4"

ENV EXT_PARALLEL=${EXT_PARALLEL} \
    MAX_JOBS=${MAX_JOBS} \
    CMAKE_BUILD_PARALLEL_LEVEL=${CMAKE_BUILD_PARALLEL_LEVEL}

# 9.0 = H100 (Hopper)
RUN TORCH_CUDA_ARCH_LIST="9.0+PTX" uv run python -m pip wheel -v --no-build-isolation --wheel-dir /opt/wheelhouse/9.0 \
    "git+https://github.com/thu-ml/SageAttention.git@${SAGEATTENTION_REF}"

# 12.0 = RTX 5090, RTX PRO 6000
RUN TORCH_CUDA_ARCH_LIST="12.0" uv run python -m pip wheel -v --no-build-isolation --wheel-dir /opt/wheelhouse/12.0 \
    "git+https://github.com/thu-ml/SageAttention.git@${SAGEATTENTION_REF}"

#
# Runtime
#
FROM base AS runtime

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HOME=/cache-volume/hf
ENV FRAMEPACK_RUNTIME_TARGET=studio

# Install dependencies.
# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libmagic1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

# Copy the virtual environment from the builder stage
# and the source code.
COPY ./ ./
COPY --link --from=builder /app/.venv ./.venv

# Copy sageattention
COPY --from=sageattention_builder /opt/wheelhouse /opt/wheelhouse

#
COPY start.sh ./
RUN chmod +x /app/start.sh

# Cache for models
VOLUME /cache-volume

# Gradio port
EXPOSE 7860

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/start.sh"]

# CMD ["uv", "run", "studio.py"]
