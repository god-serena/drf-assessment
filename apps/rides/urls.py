from .views import RideViewSet, NaiveRideViewSet
from rest_framework.routers import DefaultRouter

rider_router = DefaultRouter()
naive_router = DefaultRouter()

rider_router.register(r'rides', RideViewSet, basename = 'rides')
naive_router.register(r'naive', NaiveRideViewSet, basename = 'naive-rides')

urlpatterns = rider_router.urls + naive_router.urls