from .views import RideViewSet, NaiveRideViewSet, RideEventViewSet
from rest_framework.routers import DefaultRouter

rider_router = DefaultRouter()
naive_router = DefaultRouter()

rider_router.register(r'rides', RideViewSet, basename = 'rides')
rider_router.register(r'ride-events', RideEventViewSet, basename = 'ride-events')
naive_router.register(r'naive', NaiveRideViewSet, basename = 'naive-rides')

urlpatterns = rider_router.urls + naive_router.urls