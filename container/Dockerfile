# Mass Flood Watch: one image for laptop, GitHub Actions and Turing (Apptainer: apptainer build mfw.sif docker://ghcr.io/horus331/mass-flood-watch:<tag>).
# ADR-004. Python packages are pinned in container/requirements.lock (made by container.yml from requirements.in). LISFLOOD-FP 8.2 is built
# from source by sim/colab/w9_lisflood.py at run time (CPU here; CUDA on Turing), with the build tools below already present.
FROM python:3.11-slim-bookworm
RUN apt-get update -q && DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends \
      build-essential cmake git libnetcdf-dev netcdf-bin libnuma-dev libeccodes-dev time ca-certificates && rm -rf /var/lib/apt/lists/*
COPY container/requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock
WORKDIR /work
ENV PYTHONUNBUFFERED=1
LABEL org.opencontainers.image.source=https://github.com/Horus331/mass-flood-watch
LABEL org.opencontainers.image.description="Mass Flood Watch model environment (LISFLOOD-FP build tools + pinned Python)"
