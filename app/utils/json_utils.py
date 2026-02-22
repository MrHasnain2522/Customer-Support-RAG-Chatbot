"""
JSON utility functions
"""
import json
from datetime import datetime, date
from decimal import Decimal


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling special types"""
    
    def default(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        return super().default(obj)


def safe_json_dumps(data, **kwargs):
    """
    Safely serialize data to JSON
    
    Args:
        data: Data to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        str: JSON string
    """
    return json.dumps(data, cls=CustomJSONEncoder, **kwargs)


def safe_json_loads(json_string):
    """
    Safely deserialize JSON string
    
    Args:
        json_string: JSON string to deserialize
        
    Returns:
        Deserialized data or None on error
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None


def format_json_response(data, status='success', message=None):
    """
    Format consistent JSON response
    
    Args:
        data: Response data
        status: Response status ('success' or 'error')
        message: Optional message
        
    Returns:
        dict: Formatted response
    """
    response = {
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return response