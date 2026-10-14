FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim

WORKDIR /app
RUN useradd -m -u 1000 appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY main.py .
COPY storefront.html .
COPY admin.html .

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PORT=8081

EXPOSE 8081

HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8081/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
