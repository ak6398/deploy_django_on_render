"""
Performance monitoring middleware for Django
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()
        return None

    def process_response(self, response):
        if hasattr(request := self.request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log slow requests (> 500ms)
            if duration > 0.5:
                logger.warning(
                    f"SLOW REQUEST: {request.method} {request.path} "
                    f"took {duration:.2f}s | Status: {response.status_code}"
                )
            
            # Add timing header
            response['X-Response-Time'] = f"{duration:.3f}s"
            
            # Log all API requests
            if '/api/' in request.path:
                logger.info(
                    f"API: {request.method} {request.path} "
                    f"- {duration:.3f}s - Status: {response.status_code}"
                )
        
        return response
