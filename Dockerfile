FROM python:3.13

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD pyproject.toml uv.lock README.md /app/

WORKDIR /app

RUN uv sync --frozen

ADD . /app

WORKDIR /app/student_schedule_bot

ENTRYPOINT [ "uv", "run", "bot.py" ]
