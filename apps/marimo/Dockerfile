FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN useradd -m -u 1000 user

ENV PATH="/home/user/.local/bin:$PATH"
ENV UV_SYSTEM_PYTHON=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN uv pip install -r requirements.txt

COPY --chown=user . /app

RUN mkdir -p /app/__marimo__ && \
    chown -R user:user /app && \
    chmod -R 755 /app

USER user

CMD ["python", "server.py"]
