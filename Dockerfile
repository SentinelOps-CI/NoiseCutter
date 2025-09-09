# Multi-stage for minimal runtime
FROM python:3.12-slim AS base

ENV PATH="/root/.local/bin:${PATH}"
RUN pip install --no-cache-dir --upgrade pip

FROM base AS builder
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY noisecutter ./noisecutter
COPY policy ./policy
COPY converters ./converters
COPY docs ./docs
COPY recipes ./recipes
COPY examples ./examples
RUN pip install --no-cache-dir build && python -m build

FROM base AS runtime
WORKDIR /app
# Install tools (pinned)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin v1.16.0
# Install noisecutter wheel
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -f /tmp/*.whl

ENTRYPOINT ["python", "-m", "noisecutter"]

