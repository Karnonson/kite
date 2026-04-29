# syntax=docker/dockerfile:1.4
FROM mcr.microsoft.com/devcontainers/universal:2-linux

# The upstream image currently ships a stale Yarn apt source that breaks
# `apt-get update` inside devcontainer feature installers.
RUN rm -f /etc/apt/sources.list.d/yarn.list
