from rest_framework_nested import routers
from rest_framework import routers
from .views import *

parent_router = routers.DefaultRouter()
parent_router.register(r'students', StudentViewSet, basename='students')


urlpatterns = [
    
] + parent_router.urls