FROM python:3.12-slim as builder
RUN pip install uv
WORKDIR /app
COPY pyproject.toml .
RUN uv pip install --system -e .

FROM python:3.12-slim as runtime
RUN useradd -m appuser
USER appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY . .
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
HEALTHCHECK CMD curl -f http://localhost:8000/health
