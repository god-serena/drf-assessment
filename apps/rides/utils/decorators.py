import functools
import re
from django.conf import settings
from rest_framework.exceptions import ValidationError

def validate_query_params(serializer):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            view = args[0]
            request = args[1]
            query_params = request.query_params
            paginator = getattr(view, 'pagination_class', None)
            request.validated_query_params = {}

            extra = list()
            if paginator:   
                pattern = re.compile(r'^\w+_query_param$')
                matched = list(filter(pattern.search, dir(paginator)))
                extra.extend([getattr(paginator, x) for x in matched if getattr(paginator, x) not in (None, '')])

            if settings.DEBUG:
                extra.append('format')
            
            if query_params:
                data = {
                    name: value
                    for name, value in query_params.items()
                    if value not in (None, '')
                }
                
                serialized = serializer(context={'view': view}, data=data)
                initial = set(serialized.initial_data.keys())
                allowed = set(serialized.fields.keys())
                allowed.update(extra)
                invalid = initial.difference(allowed)

                if invalid:
                    raise ValidationError(f'Invalid query params: {list(invalid)}')
                
                serialized.is_valid(raise_exception = True)
                request.validated_query_params = serialized.validated_data
            return func(*args, **kwargs)
        return wrapper 
    return decorator