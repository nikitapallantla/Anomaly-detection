import logging, os, requests, time, json
from flask import Flask, jsonify
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

SERVICE_NAME = "notification-service"             # Change this for each file
NEXT_SERVICE_URL = "http://127.0.0.1:5007/process" # Change this for each file
PORT = 5006  

# ==========================================
# STEP 2: DIRECT-TO-DISK LOGGING (FAILSAFE)
# ==========================================
LOG_DIR = r"C:\Anomaly_Logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, f"{SERVICE_NAME}.log")

def write_failsafe_log(t_id, latency):
    """Bypasses standard logging to ensure data is written to disk instantly."""
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "service": SERVICE_NAME,
        "trace_id": t_id,
        "latency_ms": latency,
        "status": "success"
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# ==========================================
# STEP 3: OPENTELEMETRY SETUP
# ==========================================
resource = Resource(attributes={"service.name": SERVICE_NAME})
provider = TracerProvider(resource=resource)
# Sends data to Jaeger immediately
provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317")))
trace.set_tracer_provider(provider)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# ==========================================
# STEP 4: MAIN ROUTE
# ==========================================
@app.route("/process")
def process():
    start_time = time.time()
    
    # Extract Trace ID
    current_span = trace.get_current_span()
    t_id = format(current_span.get_span_context().trace_id, '032x')
    
    # Request Chaining
    res_data = {"status": "end_of_chain"}
    if NEXT_SERVICE_URL:
        try:
            response = requests.get(NEXT_SERVICE_URL, timeout=3)
            res_data = response.json()
        except Exception as e:
            res_data = {"error": f"Downstream service unavailable: {str(e)}"}

    latency = round((time.time() - start_time) * 1000, 2)
    
    # --- WRITE LOG DIRECTLY TO FILE ---
    write_failsafe_log(t_id, latency)
    
    return jsonify({"service": SERVICE_NAME, "trace_id": t_id, "next": res_data})

if __name__ == "__main__":
    print(f"--- {SERVICE_NAME} starting on port {PORT} ---")
    app.run(host="127.0.0.1", port=PORT, threaded=True)