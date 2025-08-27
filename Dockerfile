#
# Base
#
# `cudnn-devel` is required to compile `flash-attn` and others.
FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04 AS base
ENV DEBIAN_FRONTEND=noninteractive

ENV UV_CACHE_DIR=/var/cache/uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_FROZEN=1
ENV UV_NO_EDITABLE=1

# Update ca-certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* && apt-get clean
RUN update-ca-certificates

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /uvx /bin/

# Install Python
RUN --mount=type=cache,target=/var/cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
        uv python install

# Project directory
WORKDIR /app

#
# Builder
#
FROM base AS builder

# Install APT cache and packages
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
        apt update && apt-get install -y --no-install-recommends \
         build-essential

# Install dependencies
RUN --mount=type=cache,target=/var/cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
        uv venv --relocatable && \
        uv sync --extra sage --no-install-project --no-dev

#
# Runtime
#
FROM base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HOME=/cache-volume

# Install required packages
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

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Cache for models
VOLUME /cache-volume

# Gradio port
EXPOSE 7860

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uv", "run", "studio.py"]
