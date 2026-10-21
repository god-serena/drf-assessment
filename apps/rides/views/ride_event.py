from rest_framework.viewsets import ModelViewSet

from ..models import RideEvent
from ..serializers import BaseRideEventSerializer
from apps.users.permissions import AdministratorPermission


class RideEventViewSet(ModelViewSet):
    permission_classes = [AdministratorPermission]
    queryset = RideEvent.objects.all()
    serializer_class = BaseRideEventSerializer
