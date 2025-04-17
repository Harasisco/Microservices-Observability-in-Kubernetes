from flask import Flask, jsonify, request
import hashlib, os, time

# ---- OpenTelemetry ----
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

RESOURCE = Resource.create({"service.name": "hash-service"})
COLLECTOR_ENDPOINT = os.getenv("OTEL_COLLECTOR", "otel-collector-opentelemetry-collector:4317")

# --- tracing ---
trace.set_tracer_provider(TracerProvider(resource=RESOURCE))
span_exporter = OTLPSpanExporter(endpoint=COLLECTOR_ENDPOINT, insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(span_exporter))
tracer = trace.get_tracer(__name__)

# --- metrics ---
metric_exporter = OTLPMetricExporter(endpoint=COLLECTOR_ENDPOINT, insecure=True)
reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader], resource=RESOURCE))
meter = metrics.get_meter(__name__)
req_counter   = meter.create_counter("http_requests_total")
err_counter   = meter.create_counter("http_requests_errors")
lat_histogram = meter.create_histogram("http_request_duration_ms")

# ---- Flask app ----
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/hash", methods=["POST"])
def generate_hash():
    start = time.time()
    try:
        input_text = request.get_data(as_text=True)
        if not input_text:
            err_counter.add(1)
            return jsonify({"error": "Empty input"}), 400

        sha256_hash = hashlib.sha256(input_text.encode("utf-8")).hexdigest()
        return jsonify({"hash": sha256_hash})
    finally:
        req_counter.add(1)
        lat_histogram.record((time.time() - start) * 1000)

@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("APP_PORT", 8080)))
