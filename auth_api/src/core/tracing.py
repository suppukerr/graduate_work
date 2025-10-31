from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)
from src.core.config import settings


def setup_tracing(app: FastAPI) -> None:
    resource = Resource.create({"service.name": "auth_api"})

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(
        endpoint=f"http://{settings.otlp.host}:{settings.otlp.port}",
        insecure=settings.otlp.insecure
    )
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    FastAPIInstrumentor.instrument_app(app)
