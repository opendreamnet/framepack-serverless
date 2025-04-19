#
# Base
#
FROM nvidia/cuda:12.6.0-cudnn-devel-ubuntu24.04 AS base
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3.10

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

# Install Python
RUN uv python install ${PYTHON_VERSION}

#
# Builder
#
FROM base AS builder
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/var/cache/uv

# Install APT cache and packages
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && apt-get install -y \
        build-essential

WORKDIR /workspace

# Create the virtual environment
RUN uv venv --relocatable --python ${PYTHON_VERSION}

# Install dependencies
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/var/cache/uv \
  uv sync --extra sage --frozen --no-editable

# Copy the source code and build it
# COPY ./ ./

# RUN --mount=type=cache,target=/var/cache/uv \
#   uv sync --extra sage --frozen --no-editable

#
# Runtime
#
FROM base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install required packages
# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    libgl1-mesa-dev \
    libglib2.0-0
RUN apt-get clean && apt-get autoclean

# Copy the virtual environment from the builder stage
# and the source code.
WORKDIR /workspace
COPY ./ ./
COPY --link --from=builder /workspace/.venv ./.venv

# Cache for models
VOLUME /root/.cache

# Gradio port
EXPOSE 7860

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uv", "run", "demo_gradio.py"]
