from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'chat', ChatAPIViewSet, basename='chat')

urlpatterns = [
    path('test/', TestAPIView.as_view(), name='ai-test'),
    path('recommendations/', StudyRecommendationAPIView.as_view(), name='ai-recommendations'),
    # path('questions/', QuestionGenerationAPIView.as_view(), name='ai-questions'),
] + router.urls
