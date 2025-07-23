from django.urls import path
from .views import ChatAPIView, StudyRecommendationAPIView, TestAPIView

urlpatterns = [
    path('test/', TestAPIView.as_view(), name='ai-test'),
    path('chat/', ChatAPIView.as_view(), name='ai-chat'),
    # path('questions/', QuestionGenerationAPIView.as_view(), name='ai-questions'),
    path('recommendations/', StudyRecommendationAPIView.as_view(), name='ai-recommendations'),
]
