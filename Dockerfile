# syntax=docker/dockerfile:1
# Multi-stage build for minimal runtime image
FROM python:3.12-slim AS base

ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir --upgrade pip

FROM base AS builder
WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY noisecutter ./noisecutter
COPY policy ./policy
COPY docs ./docs
COPY examples ./examples

RUN pip install --no-cache-dir build && python -m build

FROM base AS runtime
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ADD --checksum=sha256:38bf84931e898d4d01c39fc806f89ae3eebac56313978dacd96156f1f9f85bc7 \
    https://github.com/anchore/syft/releases/download/v1.16.0/syft_1.16.0_linux_amd64.tar.gz \
    /tmp/syft.tgz
RUN tar -xzf /tmp/syft.tgz -C /usr/local/bin syft && rm -f /tmp/syft.tgz && chmod +x /usr/local/bin/syft

COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm -f /tmp/*.whl

RUN groupadd -r noisecutter && useradd -r -g noisecutter noisecutter
USER noisecutter

WORKDIR /workspace

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -m noisecutter --help > /dev/null || exit 1

ENTRYPOINT ["python", "-m", "noisecutter"]
