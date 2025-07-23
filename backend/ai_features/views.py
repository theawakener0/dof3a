from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import ChatRequestSerializer, StudyRecommendationSerializer
from .ai_models import chatmodel, generate_knockout_questions, generate_study_recommendations
import logging

logger = logging.getLogger(__name__)


class TestAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({
            'message': 'AI Features API is working!',
            'available_endpoints': {
                'chat': '/api/ai/chat/ (POST, requires authentication)',
                'recommendations': '/api/ai/recommendations/ (POST, requires authentication)',
                'test': '/api/ai/test/ (GET, no authentication)'
            },
            'timestamp': '2025-07-22',
            'status': 'active'
        }, status=status.HTTP_200_OK)


class ChatAPIViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRequestSerializer

    @action(detail=False, methods=['post'], url_path='generate')
    def chat(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user_input = serializer.validated_data['user_input']
                conversation_context = serializer.validated_data.get(
                    'conversation_context', '')
                user_id = str(request.user.id)

                result = chatmodel(
                    user_input=user_input,
                    user_id=user_id,
                    conversation_context=conversation_context
                )

                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error in chat generation: {str(e)}")
                return Response(
                    {'error': 'Chat generation failed', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudyRecommendationAPIView(APIView):
    """API endpoint for generating study recommendations"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StudyRecommendationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                subject = serializer.validated_data.get('subject', None)
                user_id = request.user.id

                result = generate_study_recommendations(
                    user_id=user_id,
                    subject=subject
                )

                return Response(result, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Error in study recommendation API: {str(e)}")
                return Response(
                    {'error': 'Failed to generate study recommendations',
                        'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class QuestionGenerationAPIView(APIView):
#     """API endpoint for generating quiz questions"""
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = QuestionGenerationSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 subject = serializer.validated_data['subject']
#                 grade_level = serializer.validated_data['grade_level']
#                 difficulty = serializer.validated_data.get('difficulty', 'medium')
#                 num_questions = serializer.validated_data.get('num_questions', 5)
#                 user_id = request.user.id

#                 # Call the AI question generation model
#                 result = generate_knockout_questions(
#                     subject=subject,
#                     grade_level=grade_level,
#                     difficulty=difficulty,
#                     num_questions=num_questions,
#                     user_id=user_id
#                 )

#                 return Response(result, status=status.HTTP_200_OK)

#             except Exception as e:
#                 logger.error(f"Error in question generation API: {str(e)}")
#                 return Response(
#                     {'error': 'Failed to generate questions', 'details': str(e)},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
