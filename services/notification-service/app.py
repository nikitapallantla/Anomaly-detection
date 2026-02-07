import logging
import os
from flask import Flask, jsonify
import requests
from pythonjsonlogger import jsonlogger
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# --- 1. ACTUAL LOGGING TO FILE ---
# This creates the physical file with Trace IDs required by the professor
log_dir = "/logs"
os.makedirs(log_dir, exist_ok=True)
service_name = os.getenv('SERVICE_NAME', 'service')
logger = logging.getLogger()
log_handler = logging.FileHandler(f"{log_dir}/{service_name}.log")

# Formatter automatically injects trace_id and span_id into every log line
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(trace_id)s %(span_id)s')
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# --- 2. OPENTELEMETRY SETUP ---
resource = Resource(attributes={"service.name": service_name})
provider = TracerProvider(resource=resource)
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

app = Flask(__name__)
# FlaskInstrumentor tracks incoming requests
FlaskInstrumentor().instrument_app(app)
# RequestsInstrumentor ensures Trace IDs are passed to the next service (Fixes Jaeger) 
RequestsInstrumentor().instrument()

@app.route("/process")
def process():
    current_span = trace.get_current_span()
    t_id = format(current_span.get_span_context().trace_id, '032x')
    
    logger.info(f"{service_name} is processing", extra={'trace_id': t_id})
    
    # Example logic to call the next microservice in the chain
    next_svc = os.getenv("NEXT_SERVICE")
    if next_svc:
        try:
            requests.get(f"http://{next_svc}:5000/process")
        except Exception as e:
            logger.error(f"Failed to call {next_svc}", extra={'trace_id': t_id})

    return jsonify({"status": "success", "service": service_name, "trace_id": t_id})

if __name__ == "__main__":
    # Ensure port matches your docker-compose mappings
    app.run(host="0.0.0.0", port=5000)