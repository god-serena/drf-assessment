from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import User
from ..permissions import AdministratorPermission
from ..serializers import BaseUserSerializer


class UserViewSet(ModelViewSet):
    permission_classes = [AdministratorPermission]
    serializer_class = BaseUserSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

