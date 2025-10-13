FROM python:3.14

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

WORKDIR /app

# QOL for bash:
# - Enable color support for `ls` command and add `--la` option
RUN echo "alias ls='ls --la --color=auto'" >> ~/.bashrc
