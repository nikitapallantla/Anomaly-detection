FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-flask opentelemetry-exporter-otlp
EXPOSE 5008
CMD ["python", "app.py"]