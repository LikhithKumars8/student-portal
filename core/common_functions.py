from .constants import REQUEST_INDEX
from datetime import datetime
from core.api_logger import api_logging
from core.response_format import message_response
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from functools import wraps
from django.db.models import Q


def api_exception_handler(api_name, is_staticmethod=True):
    """
    Decorator to catch api exception
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = None
            # Determine the position of the request object
            if len(args) > REQUEST_INDEX:
                if is_staticmethod:
                    request = args[0]
                else:
                    request = args[1]
            elif 'request' in kwargs:
                request = kwargs['request']
            
            log_data = [f"info|| {datetime.now()}: {api_name} API called"]
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if request:
                    error_message = send_validation_error(e)
                    context = {
                        "request_url": request.META['PATH_INFO'], "error": str(e), "payload": request.data
                    }
                    log_data.append(f"info || context :{context}")
                    log_data.append("LINE_BREAK")
                    api_logger(log_data)
                    return Response(message_response(error_message), status=400)
                else:
                    # Handle the case where request is not found
                    log_data.append(f"error || request object not found in {api_name} API")
                    log_data.append("LINE_BREAK")
                    api_logger(log_data)
                    return Response({"error": "Request object not found"}, status=400)
        return wrapper
    return decorator

def send_validation_error(e):
    validation_error_message = invalid_input
    if isinstance(e, ValidationError):
        error = e.args[0]
        if 'errors' in error:
            validation_error_message = error.get("errors")
        else:
            validation_error_message = error.get('message')
    return validation_error_message

def check_invalid(fields, message=None):
    if None in fields:
        if not message:
            message = 'Mandatory fields must be provided'
        raise ValidationError({'errors': message})
    
def create_api_key():
    from rest_framework_api_key.models import APIKey
    APIKey.objects.create_key(name="my-api-key")
    
def get_sorted(sort):
    # Default sort by
    sort_by = '-id'
    if sort is not None:
        sort_by = '-' + \
            sort['field'] if sort['order'] == 'DESC' else sort['field']

    return sort_by

def get_query_and_sort_value(filters_dictionary, filters, sort, query):
    if filters:
        for each_filter in filters:
            # get the filter function from the dictionary and apply it to the query
            filter_function = filters_dictionary.get(each_filter.get('field'))
            if filter_function:
                query &= filter_function(each_filter.get('field'), each_filter.get('value'))
    # Default is_active condition need to be added
    query &= Q(is_active=True)

    # Sorting
    sort_by = get_sorted(sort)

    return query, sort_by