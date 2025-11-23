import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class AjaxDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if request is AJAX but response is HTML (likely error or redirect)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            content_type = response.get("Content-Type", "")
            if content_type.startswith("text/html"):
                logger.error(
                    "AJAX request returned HTML content; path: %s, status: %s, content starts with: %s",
                    request.path,
                    response.status_code,
                    response.content[:100],
                )
        return response
