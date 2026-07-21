import re
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from apps.core.context import correlation_id_var

VALID_CORRELATION_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


class CorrelationIdMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        supplied = request.headers.get("X-Correlation-ID", "")
        correlation_id = supplied if VALID_CORRELATION_ID.fullmatch(supplied) else str(uuid.uuid4())
        token = correlation_id_var.set(correlation_id)
        request.correlation_id = correlation_id
        try:
            response = self.get_response(request)
            response["X-Correlation-ID"] = correlation_id
            return response
        finally:
            correlation_id_var.reset(token)
