# jaeger_example.py
from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor


def config_opentelemetry(app, service_name, agent_host, agent_port):
    trace.set_tracer_provider(TracerProvider())

    RequestsInstrumentor().instrument()
    ElasticsearchInstrumentor().instrument()
    RedisInstrumentor().instrument()
    FlaskInstrumentor().instrument_app(app)

    jaeger_exporter = jaeger.JaegerSpanExporter(
        service_name=service_name, agent_host_name=agent_host, agent_port=agent_port,
    )

    trace.get_tracer_provider().add_span_processor(
        BatchExportSpanProcessor(jaeger_exporter)
    )
