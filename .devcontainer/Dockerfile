FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive

# System deps + Node.js LTS
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git sudo ca-certificates gnupg build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv via official installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Claude Code globally
RUN npm install -g @anthropic-ai/claude-code

# Create a non-root dev user
RUN useradd -m -s /bin/bash -G sudo dev \
    && echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /workspace
USER dev

# Make uv tools available on PATH for dev user
ENV PATH="/home/dev/.local/bin:$PATH"

# Install pre-commit as the dev user so it lands in /home/dev/.local/bin
RUN uv tool install pre-commit
