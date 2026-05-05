# syntax=docker/dockerfile:1.4
FROM mcr.microsoft.com/devcontainers/universal:2-linux

# The upstream image currently ships a stale Yarn apt source that breaks
# `apt-get update` inside devcontainer feature installers. Install lightweight
# browser/terminal helpers used by AI runners, then clear the apt cache.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        bubblewrap \
        socat \
    && rm -rf /var/lib/apt/lists/*
