from django.urls import path
from .views import ChatAPIView, StudyRecommendationAPIView

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='ai-chat'),
    # path('questions/', QuestionGenerationAPIView.as_view(), name='ai-questions'),
    path('recommendations/', StudyRecommendationAPIView.as_view(), name='ai-recommendations'),
]
