from django.contrib.auth.backends import ModelBackend

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        
        if user and user.is_superuser:
            return None
        
        return user