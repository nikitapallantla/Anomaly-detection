import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# 1. Setup the name of the service
resource = Resource(attributes={"service.name": "manual-tester"})
provider = TracerProvider(resource=resource)

# 2. Point to your LOCAL Jaeger (Port 4317 is the OTLP door)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

# 3. Create the trace
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("Manual-Test-Span") as span:
    span.set_attribute("test.status", "it_worked")
    print("🚀 Sending trace to Jaeger...")
    time.sleep(1) # Simulating "work"
    print("✅ Done!")

# Important: Shutdown to flush the data to Jaeger immediately
provider.shutdown()