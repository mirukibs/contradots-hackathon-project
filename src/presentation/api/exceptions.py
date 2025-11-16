"""
Custom exception handling for REST API endpoints.

This module provides customized exception handling for Django REST Framework
to ensure consistent error responses across all API endpoints.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied as DRFPermissionDenied
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that returns consistent error responses.
    
    Args:
        exc: The exception that was raised
        context: Additional context about the request and view
        
    Returns:
        Response object with standardized error format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response for known DRF exceptions
        custom_response_data = {
            'error': get_error_type(exc),
            'message': get_error_message(exc, response.data),
            'status_code': response.status_code,
        }
        
        # Add details if available
        if hasattr(response, 'data') and isinstance(response.data, dict):
            if 'detail' not in response.data:
                custom_response_data['details'] = response.data
        
        response.data = custom_response_data
        
    else:
        # Handle Django exceptions that DRF doesn't handle by default
        if isinstance(exc, Http404):
            response = Response(
                {
                    'error': 'NOT_FOUND',
                    'message': 'The requested resource was not found.',
                    'status_code': status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, PermissionDenied):
            response = Response(
                {
                    'error': 'PERMISSION_DENIED',
                    'message': 'You do not have permission to perform this action.',
                    'status_code': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN
            )
        elif isinstance(exc, DjangoValidationError):
            response = Response(
                {
                    'error': 'VALIDATION_ERROR',
                    'message': 'The request data is invalid.',
                    'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                    'status_code': status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Handle unexpected exceptions
            logger.error(f"Unexpected exception in API: {type(exc).__name__}: {str(exc)}", exc_info=True)
            
            response = Response(
                {
                    'error': 'INTERNAL_SERVER_ERROR',
                    'message': 'An unexpected error occurred. Please try again later.',
                    'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Log the error for monitoring
    if response.status_code >= 500:
        logger.error(f"Server error in API: {type(exc).__name__}: {str(exc)}", exc_info=True)
    elif response.status_code >= 400:
        logger.warning(f"Client error in API: {type(exc).__name__}: {str(exc)}")
    
    return response


def get_error_type(exc):
    """
    Get a standardized error type string for the exception.
    
    Args:
        exc: The exception
        
    Returns:
        String representing the error type
    """
    if isinstance(exc, AuthenticationFailed):
        return 'AUTHENTICATION_FAILED'
    elif isinstance(exc, (PermissionDenied, DRFPermissionDenied)):
        return 'PERMISSION_DENIED'
    elif isinstance(exc, ValidationError):
        return 'VALIDATION_ERROR'
    elif isinstance(exc, Http404):
        return 'NOT_FOUND'
    else:
        # Map other common DRF exceptions
        exc_name = type(exc).__name__
        return exc_name.upper().replace('EXCEPTION', '').replace('ERROR', '_ERROR')


def get_error_message(exc, response_data):
    """
    Get a human-readable error message from the exception and response data.
    
    Args:
        exc: The exception
        response_data: DRF response data
        
    Returns:
        Human-readable error message
    """
    # Try to get message from response data first
    if isinstance(response_data, dict):
        if 'detail' in response_data:
            detail = response_data['detail']
            if isinstance(detail, str):
                return detail
            elif isinstance(detail, list) and detail:
                return str(detail[0])
        elif 'message' in response_data:
            return response_data['message']
    
    # Try to get message from exception
    if hasattr(exc, 'detail'):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        elif isinstance(detail, list) and detail:
            return str(detail[0])
        elif isinstance(detail, dict):
            # Return first error message from dict
            for key, value in detail.items():
                if isinstance(value, list) and value:
                    return f"{key}: {value[0]}"
                else:
                    return f"{key}: {value}"
    
    # Fallback to string representation
    return str(exc) if str(exc) else f"An error occurred: {type(exc).__name__}"