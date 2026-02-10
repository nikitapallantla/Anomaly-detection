import os
import time
import json
import requests

from flask import Flask, jsonify

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor



SERVICE_NAME = "notification-service"             # Change this for each file
NEXT_SERVICE_URL = "http://fraud-service:5007/process" # Change this for each file
PORT = 5006  
LOG_DIR = r"C:\Users\nikit\OneDrive\Desktop\Anomaly_Logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, f"{SERVICE_NAME}.log")


# def write_failsafe_log(trace_id, latency):
#     log_entry = {
#         "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
#         "service": SERVICE_NAME,
#         "trace_id": trace_id,
#         "latency_ms": latency,
#         "status": "success"
#     }

#     with open(log_path, "a", encoding="utf-8") as f:
#         f.write(json.dumps(log_entry) + "\n")
#         f.flush()

#     print(f"✅ {SERVICE_NAME} LOG WRITTEN")


# -------------------------------------------------------------------
# 3. TRACING SETUP
# -------------------------------------------------------------------
resource = Resource(attributes={"service.name": SERVICE_NAME})
provider = TracerProvider(resource=resource)

try:
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint="http://jaeger:4317")
        )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
except Exception as e:
    print("Tracing failed:", e)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


# -------------------------------------------------------------------
# 4. ROUTE – THIS CALLS THE NEXT SERVICE (IF SET)
# -------------------------------------------------------------------
@app.route("/process")
def process():
    start_time = time.time()
    
    # Get Trace ID
    current_span = trace.get_current_span()
    trace_id = format(current_span.get_span_context().trace_id, "032x")

    downstream_response = None

    if NEXT_SERVICE_URL:
        try:
            # High timeout for Docker overhead
            resp = requests.get(NEXT_SERVICE_URL, timeout=40) 
            downstream_response = resp.json()
        except Exception as e:
            downstream_response = {"error": str(e)}

    latency = round((time.time() - start_time) * 1000, 2)
    
    # COMMENT THIS OUT TO PREVENT CRASHES AND SPEED UP
    # write_failsafe_log(trace_id, latency) 

    return jsonify({
        "service": SERVICE_NAME,
        "trace_id": trace_id,
        "latency_ms": latency,
        "next_service_response": downstream_response
    })

# -------------------------------------------------------------------
# 5. ENTRY POINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    # 0.0.0.0 tells Flask to listen for requests coming from outside the container
    app.run(host="0.0.0.0", port=PORT, threaded=True)