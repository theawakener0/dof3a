"""
AI Features Module

This module provides AI-powered features for the application including:
- AI Chat: Interactive chat functionality with personalized responses
- Question Generation: Generate quiz questions based on subject and difficulty
- Study Recommendations: Personalized study recommendations for users

API Endpoints:
- /api/ai/chat/ - POST: Chat with AI assistant
- /api/ai/questions/ - POST: Generate quiz questions  
- /api/ai/recommendations/ - POST: Get study recommendations

All endpoints require user authentication.
Make sure to set GOOGLE_API_KEY in your environment file.
"""

default_app_config = 'ai_features.apps.AiFeaturesConfig'
