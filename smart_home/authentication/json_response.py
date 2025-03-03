from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

class JsonResponse:

    @staticmethod
    def success(message="Request was successful.", data=None, extra=None, code=200):
        """
        Standard success response.
        """
        response = {
            "status": "success",
            "code": code,
            "message": message,
            "data": data or {},
        }

        if extra:
            response.update(extra)

        return Response(response, status=code)
    
    
    @staticmethod
    def error(message="An error occurred.", errors=None, code=400, extra=None):
        if errors:
            logger.error(f"Error: {message} - Details: {errors}")
        response = {
            "status": "error",
            "code": code,
            "message": message,
            "errors": errors or [],
        }

        if extra:
            response.update(extra)

        return Response(response, status=code)
    
    @staticmethod
    def partial(message="Request partially succeeded.", data=None, extra=None, code=206):
        """
        Standard partial response.
        """
        response = {
            "status": "partial",
            "code": code,
            "message": message,
            "data": data or {},
        }

        if extra:
            response.update(extra)

        return Response(response, status=code)