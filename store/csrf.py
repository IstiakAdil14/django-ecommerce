from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import CsrfViewMiddleware

class AjaxCSRFMiddleware(CsrfViewMiddleware):
    def _reject(self, request, reason):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'CSRF token missing or incorrect.'}, status=403)
        return super()._reject(request, reason)
