"""
String and Integer Conversion Utilities

This module provides functions to convert between string and integer values
with proper error handling and validation.
"""
import uuid

def string_to_int(value):
    """
    Convert a string value to an integer.
    
    Args:
        value: The string value to convert to integer
        
    Returns:
        int: The converted integer value
        
    Raises:
        ValueError: If the string cannot be converted to an integer
        TypeError: If the input is not a string
    """
    if not isinstance(value, str):
        raise TypeError(f"Expected string, got {type(value).__name__}")
    
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f"Cannot convert '{value}' to integer: {e}")


def int_to_uuid(value):
    """
    Convert an integer value to a string.
    
    Args:
        value: The integer value to convert to string
        
    Returns:
        str: The converted string value
        
    Raises:
        TypeError: If the input is not an integer
    """
    if not isinstance(value, int):
        raise TypeError(f"Expected integer, got {type(value).__name__}")
    
    return uuid.UUID(int=value)


def safe_uuid_to_int(value, default=0):
    """
    Safely convert a string value to an integer with a default fallback.
    
    Args:
        value: The string value to convert to integer
        default: The default value to return if conversion fails (default: 0)
        
    Returns:
        int: The converted integer value or the default value
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_int_to_uuid(value, default="0"):
    """
    Safely convert an integer value to a string with a default fallback.
    
    Args:
        value: The integer value to convert to string
        default: The default value to return if conversion fails (default: "0")
        
    Returns:
        str: The converted string value or the default value
    """
    try:
        return int_to_uuid(value)
    except TypeError:
        return default


