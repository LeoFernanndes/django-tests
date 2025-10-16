import os

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor



def setup_telemetry():
    # Define service name and environment
    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "django-api"),
        "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("ENVIRONMENT", "development")
    })
    
    # Setup Tracing
    trace_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(trace_provider)
    
    # Configure OTLP exporter for traces
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
        insecure=True  # Set to False in production with proper TLS
    )
    
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace_provider.add_span_processor(span_processor)
    
    # Setup Metrics
    metric_reader = PeriodicExportingMetricReader(
        exporter=OTLPMetricExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
            insecure=True
        ),
        export_interval_millis=60000  # Export metrics every minute
    )
    
    metric_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader]
    )
    metrics.set_meter_provider(metric_provider)
    
    # Instrument Django
    DjangoInstrumentor().instrument(trace_provider=trace_provider, is_sql_commentor_enabled=True)
    
    # Instrument other libraries
    Psycopg2Instrumentor().instrument(trace_provider=trace_provider, 
                                      skip_dep_check=True, 
                                      enable_commenter=True,
                                      enable_attribute_commenter=True,
                                      capture_parameters=False)
    
    SQLite3Instrumentor().instrument()