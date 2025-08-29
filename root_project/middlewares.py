import logging

from django.utils.deprecation import MiddlewareMixin


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('my_debugger')

    def __call__(self, request):
        # Log request details
        # TODO: Note that user here always comes as Annonymous. We must see DRF  
        # DEFAULT_AUTHENTICATION_CLASSES to understand when user is appended to the request 
        self.logger.info(f"Request: {request.user} {request.method} {request.path}")
        if request.body:
            self.logger.debug(f"Request Body: {request.body.decode('utf-8')}")

        response = self.get_response(request)

        # Log response details
        self.logger.info(f"Response: {request.user} {response.status_code}")        
        return response
