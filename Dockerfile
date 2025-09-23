# Multi-stage build for minimal runtime image
FROM python:3.12-slim AS base

# Set environment variables
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip

# Builder stage
FROM base AS builder
WORKDIR /app

# Copy package files
COPY pyproject.toml README.md LICENSE ./
COPY noisecutter ./noisecutter
COPY policy ./policy
COPY converters ./converters
COPY docs ./docs
COPY recipes ./recipes
COPY examples ./examples

# Build the package
RUN pip install --no-cache-dir build && python -m build

# Runtime stage
FROM base AS runtime
WORKDIR /app

# Install system dependencies and tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install syft (pinned version for reproducibility)
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | \
    sh -s -- -b /usr/local/bin v1.16.0

# Install noisecutter wheel
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm -f /tmp/*.whl

# Create non-root user for security
RUN groupadd -r noisecutter && useradd -r -g noisecutter noisecutter
USER noisecutter

# Set working directory
WORKDIR /workspace

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -m noisecutter --help > /dev/null || exit 1

# Default entrypoint
ENTRYPOINT ["python", "-m", "noisecutter"]

