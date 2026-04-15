# NoiseCutter Makefile
# Provides convenient targets for development, running, and releasing

.PHONY: help dev run release clean test lint format install-deps

# Default target
help:
	@echo "NoiseCutter - Available targets:"
	@echo "  dev       - Set up local development environment"
	@echo "  run       - Run the application/CLI locally"
	@echo "  release   - Build and publish artifacts (supports dry-run)"
	@echo "  clean     - Clean build artifacts"
	@echo "  test      - Run tests"
	@echo "  lint      - Run linting"
	@echo "  format    - Format code"
	@echo "  install-deps - Install development dependencies"

# Set up local development environment
dev: install-deps
	@echo "Setting up development environment..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
	else \
		echo "pre-commit not found, skipping pre-commit hook installation"; \
	fi
	@echo "Development environment ready!"
	@echo "Run 'make run' to test the CLI"

# Install development dependencies
install-deps:
	@echo "Installing development dependencies..."
	pip install -e ".[dev]"
	@echo "Dependencies installed!"

# Run the application/CLI locally
run:
	@echo "Running NoiseCutter CLI..."
	python -m noisecutter --help

# Run tests
test:
	@echo "Running tests..."
	pytest

# Run linting
lint:
	@echo "Running linting..."
	ruff check .
	mypy noisecutter/

# Format code
format:
	@echo "Formatting code..."
	ruff format .
	ruff check --fix .

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@if exist build rmdir /s /q build
	@if exist dist rmdir /s /q dist
	@if exist *.egg-info rmdir /s /q *.egg-info
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .mypy_cache rmdir /s /q .mypy_cache
	@if exist .ruff_cache rmdir /s /q .ruff_cache
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"

# Build and publish artifacts (supports dry-run)
release: clean
	@echo "Building artifacts..."
	python -m pip install --upgrade pip build twine
	python -m build
	@echo "Build complete! Artifacts in dist/"
	@echo ""
	@echo "To publish to PyPI (dry-run):"
	@echo "  python -m twine upload --repository testpypi dist/*"
	@echo ""
	@echo "To publish to PyPI (production):"
	@echo "  python -m twine upload dist/*"
	@echo ""
	@echo "To build Docker image:"
	@echo "  docker build -t ghcr.io/noisecutter/noisecutter:latest ."
	@echo "  docker push ghcr.io/noisecutter/noisecutter:latest"

# Docker targets
docker-build:
	@echo "Building Docker image..."
	docker build -t ghcr.io/noisecutter/noisecutter:latest .

docker-run:
	@echo "Running Docker container..."
	docker run --rm ghcr.io/noisecutter/noisecutter:latest --help

# Development workflow
dev-workflow: dev test lint
	@echo "Development workflow complete!"

# Release workflow (dry-run)
release-dry-run: clean
	@echo "Dry-run release process..."
	python -m pip install --upgrade pip build twine
	python -m build
	@echo "Dry-run complete! Check dist/ for artifacts"
	@echo "Run 'make release' to proceed with actual publishing"
