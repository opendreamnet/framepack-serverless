# syntax = devthefuture/dockerfile-x
FROM ./Dockerfile

ENV HF_HOME=/runpod-volume/hf
ENV FRAMEPACK_HOME=/runpod-volume/framepack
ENV FRAMEPACK_BIN_DIR=/runpod-volume/framepack/bin
ENV FRAMEPACK_RUNTIME_TARGET=serverless

ENTRYPOINT []
CMD ["/app/start.sh"]

# CMD ["uv", "run", "serverless.py"]