# syntax = devthefuture/dockerfile-x
FROM ./Dockerfile

RUN --mount=type=cache,target=/var/cache/uv \
  uv sync --extra sage --extra runpod --no-dev

ENTRYPOINT []
CMD ["uv", "run", "rp_handler.py"]