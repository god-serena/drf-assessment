from rest_framework.viewsets import ModelViewSet

from ..models import User
from ..permissions import AdministratorPermission
from ..serializers import BaseUserSerializer


class UserViewSet(ModelViewSet):
    permission_classes = [AdministratorPermission]
    serializer_class = BaseUserSerializer
    queryset = User.objects.all()
