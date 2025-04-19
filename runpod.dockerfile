# syntax = devthefuture/dockerfile-x
FROM ./Dockerfile

RUN --mount=type=cache,target=/var/cache/uv \
  uv sync --extra sage --extra runpod --frozen --no-editable

CMD ["uv", "run", "rp_handler.py"]