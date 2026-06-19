import functools
import logging
import uuid
from datetime import datetime, timezone
from typing import Callable

logger = logging.getLogger("metaai.tracing")

_in_memory_spans: list[dict] = []
_current_trace_id: str | None = None


def init_tracer():
    logger.info("Tracing initialized (in-memory mode)")
    return _in_memory_spans


def get_current_trace_id() -> str | None:
    return _current_trace_id


def set_current_trace_id(trace_id: str):
    global _current_trace_id
    _current_trace_id = trace_id


def create_span(
    name: str,
    span_type: str = "general",
    attributes: dict | None = None,
    parent_span_id: str | None = None,
) -> dict:
    span = {
        "span_id": str(uuid.uuid4()),
        "trace_id": _current_trace_id or str(uuid.uuid4()),
        "name": name,
        "span_type": span_type,
        "attributes": attributes or {},
        "parent_span_id": parent_span_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": None,
        "status": "started",
    }
    if _current_trace_id is None:
        set_current_trace_id(span["trace_id"])
    _in_memory_spans.append(span)
    return span


def end_span(span: dict, status: str = "ok"):
    span["end_time"] = datetime.now(timezone.utc).isoformat()
    span["status"] = status


def get_all_spans() -> list[dict]:
    return _in_memory_spans


def get_trace_spans(trace_id: str) -> list[dict]:
    return [s for s in _in_memory_spans if s["trace_id"] == trace_id]


def clear_spans():
    _in_memory_spans.clear()


def instrument_agent_execution(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        trace_id = str(uuid.uuid4())
        set_current_trace_id(trace_id)
        span = create_span(
            name=func.__name__,
            span_type="agent_execution",
            attributes={"args": str(args), "kwargs": str(kwargs)},
        )
        logger.info("Starting traced execution [%s]: %s", trace_id, func.__name__)
        try:
            result = await func(*args, **kwargs)
            end_span(span, status="ok")
            return result
        except Exception as e:
            end_span(span, status="error")
            span["attributes"]["error"] = str(e)
            logger.error("Traced execution failed [%s]: %s", trace_id, str(e))
            raise
        finally:
            set_current_trace_id(None)

    return wrapper


class TraceContext:
    def __init__(self, name: str, span_type: str = "general", attributes: dict | None = None):
        self.name = name
        self.span_type = span_type
        self.attributes = attributes or {}
        self.span: dict | None = None

    async def __aenter__(self):
        self.span = create_span(self.name, self.span_type, self.attributes)
        return self.span

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            end_span(self.span, status="error" if exc_type else "ok")
            if exc_type:
                self.span["attributes"]["error"] = str(exc_val)
