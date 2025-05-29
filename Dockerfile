#
# Base
#
FROM nvidia/cuda:12.6.0-cudnn-devel-ubuntu24.04 AS base
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3.10

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
COPY --from=ghcr.io/astral-sh/uv:0.6.17 /uv /uvx /bin/

# Install Python
RUN uv python install ${PYTHON_VERSION}

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

# Create the virtual environment
RUN uv venv --relocatable --python ${PYTHON_VERSION}

# Install dependencies
RUN --mount=type=cache,target=/var/cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
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
CMD ["uv", "run", "demo_gradio.py"]
