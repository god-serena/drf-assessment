from rest_framework.authentication import SessionAuthentication


class ApiSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        if 'HTTP_AUTHORIZATION' in request.META and request.META['HTTP_AUTHORIZATION'].startswith('Basic '):
            return
        return super().enforce_csrf(request)
