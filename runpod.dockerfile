# syntax = devthefuture/dockerfile-x
FROM ./Dockerfile

ENV HF_HOME=/runpod-volume
ENV FRAMEPACK_HOME=/runpod-volume/framepack

RUN --mount=type=cache,target=/var/cache/uv \
  uv sync --extra sage --extra runpod --no-dev

ENTRYPOINT []
CMD ["uv", "run", "serverless.py"]