FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

COPY uv.lock pyproject.toml /app/

RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

COPY --chmod=755 scripts/dev_entry /app/scripts/dev_entry/

ENTRYPOINT ["/app/scripts/dev_entry"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]