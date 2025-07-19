from rest_framework_nested import routers
from rest_framework import routers
from .views import *

student_router = routers.DefaultRouter()
student_router.register(r'students', StudentViewSet, basename='students')

posts_router = routers.DefaultRouter()
posts_router.register(r'posts', PostViewSet, basename='posts')


urlpatterns = [
    
] + student_router.urls \
    + posts_router.urls