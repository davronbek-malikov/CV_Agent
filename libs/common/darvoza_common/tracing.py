"""OpenTelemetry setup. Spans carry the envelope trace_id as an attribute so one
user request can be followed across gateway, orchestrator, agents and judge."""

import logging
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .settings import get_settings


def setup_logging(name: str) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=f'{{"t":"%(asctime)s","svc":"{name}","lvl":"%(levelname)s","log":"%(name)s","msg":"%(message)s"}}',
    )
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def setup_tracing(service: str) -> None:
    endpoint = get_settings().otel_endpoint
    provider = TracerProvider(resource=Resource.create({"service.name": service}))
    if endpoint:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")))
    trace.set_tracer_provider(provider)


@contextmanager
def span(name: str, trace_id: str = "", **attrs):
    tracer = trace.get_tracer("darvoza")
    with tracer.start_as_current_span(name) as s:
        s.set_attribute("darvoza.trace_id", trace_id)
        for k, v in attrs.items():
            s.set_attribute(f"darvoza.{k}", str(v))
        yield s
