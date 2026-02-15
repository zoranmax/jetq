# Docker Testing Guide for jetq

This guide explains how to test jetq across multiple Python versions using Docker containers.

## Prerequisites

- Docker (version 20.10 or later)
- docker-compose (version 1.29 or later)
- [Task](https://taskfile.dev/) (optional, but recommended for easier command usage)

### Installing Docker

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER  # Add yourself to docker group
# Log out and back in for group changes to take effect
```

**macOS:**
```bash
brew install --cask docker
```

**Windows:**
Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

### Installing Task (Optional, Recommended)

**macOS:**
```bash
brew install go-task
```

**Linux:**
```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
```

**Windows:**
```powershell
choco install go-task
```

Or download from https://taskfile.dev/installation/

## Quick Start

### Using Task Runner (Recommended)

If you have [Task](https://taskfile.dev/) installed, you can use these convenient commands:

```bash
# Run tests on all Python versions
task docker:test

# Run tests on a specific Python version
task docker:test:3.8
task docker:test:3.9
task docker:test:3.10
task docker:test:3.11
task docker:test:3.12
task docker:test:3.13

# Build all Docker images
task docker:build

# Open interactive shell (defaults to Python 3.11)
task docker:shell

# Open shell with specific Python version
PY_VERSION=3.10 task docker:shell

# Clean up Docker resources
task docker:clean

# View all available Docker tasks
task --list | grep docker
```

### Using test-docker.sh Script

Alternatively, use the test script directly:

### 1. Run tests on all Python versions
```bash
./test-docker.sh --all
```

### 2. Run tests on a specific Python version
```bash
./test-docker.sh 3.8
./test-docker.sh 3.10
./test-docker.sh 3.12
```

### 3. Build images and run tests
```bash
./test-docker.sh --build --all
./test-docker.sh --build 3.9
```

### 4. Open an interactive shell in a container
```bash
./test-docker.sh --shell 3.8
```

### 5. Clean up Docker resources
```bash
./test-docker.sh --clean
```

## Usage Examples

### Test on Python 3.8 (minimum supported version)
```bash
# Using Task runner
task docker:test:3.8

# Or using test-docker.sh
./test-docker.sh 3.8
```

### Test on Python 3.12 (current stable)
```bash
# Using Task runner
task docker:test:3.12

# Or using test-docker.sh
./test-docker.sh 3.12
```

### Build fresh images and test everything
```bash
# Using Task runner
task docker:build
task docker:test

# Or using test-docker.sh
./test-docker.sh --build --all
```

### Debug issues in Python 3.9
```bash
# Open a shell in the Python 3.9 container (Task runner)
PY_VERSION=3.9 task docker:shell

# Or using test-docker.sh
./test-docker.sh --shell 3.9

# Inside the container, run tests with more verbosity
pytest -vv
pytest tests/test_restful.py -v
pytest tests/integration_test.py::test_specific_function -vv
```

### Run specific test files
```bash
# Using docker-compose directly
docker-compose run --rm test-py38 pytest tests/integration_test.py -v
docker-compose run --rm test-py310 pytest tests/test_restful.py -v
```

### Run tests with coverage
```bash
docker-compose run --rm test-py312 pytest --cov=jetq --cov-report=html
```

## Manual Docker Commands

If you prefer to use Docker commands directly:

### Build an image for Python 3.10
```bash
docker-compose build test-py310
```

### Run tests in Python 3.11 container
```bash
docker-compose run --rm test-py311
```

### Open bash shell in Python 3.8 container
```bash
docker-compose run --rm test-py38 /bin/bash
```

### Run a specific test
```bash
docker-compose run --rm test-py39 pytest tests/integration_test.py -v
```

### Stop all running containers
```bash
docker-compose down
```

## Supported Python Versions

The Docker setup supports testing on:

- Python 3.8 (minimum supported)
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13 (latest)

## Customizing Tests

### Running tests with different pytest options

Edit the `command` in [docker-compose.yml](docker-compose.yml):

```yaml
services:
  test-py38:
    command: pytest -vv --tb=long  # More verbose output
```

Or override at runtime:
```bash
docker-compose run --rm test-py38 pytest -vv --tb=long
```

### Adding test dependencies

Update [requirements-dev.txt](requirements-dev.txt) and rebuild:
```bash
# Using Task runner
task docker:build
task docker:test

# Or using test-docker.sh
./test-docker.sh --build --all
```

### Testing with different data or configurations

Mount additional volumes in [docker-compose.yml](docker-compose.yml):
```yaml
volumes:
  - .:/app
  - ./test-data:/app/test-data  # Add test data directory
```

## Continuous Integration

### Using in GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v3
      
      # Option 1: Using Task runner (requires Task installation)
      - name: Install Task
        run: |
          sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
      
      - name: Build and test with Task
        run: task docker:test:${{ matrix.python-version }}
      
      # Option 2: Using docker-compose directly
      - name: Build and test Python ${{ matrix.python-version }}
        run: |
          docker-compose build test-py${{ matrix.python-version }}
          docker-compose run --rm test-py${{ matrix.python-version }}
```

### Using in GitLab CI

Create `.gitlab-ci.yml`:

```yaml
test:
  image: docker:latest
  services:
    - docker:dind
  before_script:
    # Optional: Install Task for cleaner commands
    - apk add --no-cache curl sh
    - sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
  script:
    # Using Task runner
    - task docker:test
    # Or using docker-compose directly
    # - docker-compose run --rm test-py38
    # - docker-compose run --rm test-py39
    # - docker-compose run --rm test-py310
    # - docker-compose run --rm test-py311
    # - docker-compose run --rm test-py312
```

## Troubleshooting

### Permission denied errors
```bash
# Add yourself to the docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Container won't start
```bash
# Check Docker daemon is running
sudo systemctl status docker

# Start Docker if needed
sudo systemctl start docker
```

### Build fails
```bash
# Clean up and rebuild (Task runner)
task docker:clean
task docker:build
task docker:test

# Or using test-docker.sh
./test-docker.sh --clean
./test-docker.sh --build --all
```

### Tests pass locally but fail in Docker
```bash
# Check for missing dependencies in requirements-dev.txt (Task runner)
PY_VERSION=3.8 task docker:shell

# Or using test-docker.sh
./test-docker.sh --shell 3.8

# Inside container:
pip list
pytest -v
```

### Out of disk space
```bash
# Remove unused Docker resources
docker system prune -a
```

## Performance Tips

### Speed up builds with layer caching
The Dockerfile is optimized for layer caching. Dependencies are installed before copying source code, so changes to your code don't require reinstalling packages.

### Parallel testing
Run tests on multiple versions simultaneously:
```bash
# Using Task runner in separate terminals
task docker:test:3.8 &
task docker:test:3.9 &
task docker:test:3.10 &
wait

# Or using test-docker.sh
./test-docker.sh 3.8 &
./test-docker.sh 3.9 &
./test-docker.sh 3.10 &
wait
```

### Using pre-built images
After first build, subsequent runs are fast:
```bash
# First time (builds images) - Task runner
task docker:build  # Takes a few minutes
task docker:test   # Run tests

# Or using test-docker.sh
./test-docker.sh --build --all  # Takes a few minutes

# Subsequent runs (uses cached images)
task docker:test        # Fast! (Task runner)
./test-docker.sh --all  # Fast! (test-docker.sh)
```

## Advanced Usage

### Custom test commands

```bash
# Run with verbose output
docker-compose run --rm test-py38 pytest -vv

# Run with coverage
docker-compose run --rm test-py38 pytest --cov=jetq

# Run specific test file
docker-compose run --rm test-py38 pytest tests/integration_test.py

# Run with pdb on failures
docker-compose run --rm test-py38 pytest --pdb
```

### Interactive debugging

```bash
# Start container with shell (Task runner)
PY_VERSION=3.8 task docker:shell

# Or using test-docker.sh
./test-docker.sh --shell 3.8

# Inside container:
python -m pytest tests/integration_test.py::test_where -vv
python -m pdb main.py
ipython  # if installed
```

## Files Overview

- **Taskfile.yml** - Task runner configuration with Docker test commands
- **Dockerfile** - Multi-stage Dockerfile for building test images
- **docker-compose.yml** - Orchestration for multiple Python versions
- **.dockerignore** - Files excluded from Docker context
- **test-docker.sh** - Convenience script for running tests

## See Also

- [README.md](README.md) - Main project documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [API.md](API.md) - Complete API reference
