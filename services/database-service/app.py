import os
import time
import json
from flask import Flask, jsonify
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# --- SETTINGS ---
SERVICE_NAME = "database-service"
NEXT_SERVICE_URL = "" # Change this for each file

PORT = 5008
LOG_DIR = r"C:\Users\nikit\OneDrive\Desktop\Anomaly_Logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, f"{SERVICE_NAME}.log")

# --- TRACING ---
resource = Resource(attributes={"service.name": SERVICE_NAME})
provider = TracerProvider(resource=resource)
processor = SimpleSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/process")
def process():
    start_time = time.time()
    current_span = trace.get_current_span()
    trace_id = format(current_span.get_span_context().trace_id, "032x")
    
    # Simulate database work
    time.sleep(0.05) 
    
    latency = round((time.time() - start_time) * 1000, 2)
    
    log_entry = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "service": SERVICE_NAME, "trace_id": trace_id, "latency_ms": latency, "status": "success"}
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return jsonify({"service": SERVICE_NAME, "status": "complete", "trace_id": trace_id})

if __name__ == "__main__":
    # 0.0.0.0 tells Flask to listen for requests coming from outside the container
    app.run(host="0.0.0.0", port=PORT, threaded=True)