from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat requests"""
    user_input = serializers.CharField(max_length=2000, required=True)
    conversation_context = serializers.CharField(max_length=10000, required=False, allow_blank=True)


class QuestionGenerationSerializer(serializers.Serializer):
    """Serializer for question generation requests"""
    subject = serializers.CharField(max_length=100, required=True)
    grade_level = serializers.CharField(max_length=50, required=True)
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='medium',
        required=False
    )
    num_questions = serializers.IntegerField(min_value=1, max_value=20, default=5, required=False)


class StudyRecommendationSerializer(serializers.Serializer):
    """Serializer for study recommendation requests"""
    subject = serializers.CharField(max_length=100, required=False, allow_blank=True)
