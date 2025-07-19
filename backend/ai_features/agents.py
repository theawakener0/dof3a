"""
AI Agents System for Egyptian Educational Social Media Platform

This module contains specialized AI agents for different platform features:
1. Personal Study AI Agent - Personalized learning assistance
2. Knockout Question Generator - AI-generated 1v1 competition questions
3. Content Moderation Agent - Educational content detection and filtering
4. Study Group Location Recommender - AI-powered meeting location suggestions
5. Academic Competition Agent - Fair matching and progression tracking
6. Social Learning Agent - Community interaction and peer learning

Each agent leverages user data from parserdb to provide personalized experiences.
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import parserdb
from chatai import get_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class AgentType(Enum):
    PERSONAL_TUTOR = "personal_tutor"
    KNOCKOUT_GENERATOR = "knockout_generator"
    CONTENT_MODERATOR = "content_moderator"
    LOCATION_RECOMMENDER = "location_recommender"
    COMPETITION_MANAGER = "competition_manager"
    SOCIAL_LEARNING = "social_learning"

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentType(Enum):
    POST = "post"
    REEL = "reel"
    COMMENT = "comment"
    STUDY_MATERIAL = "study_material"

class PersonalTutorAgent:
    """
    AI Agent for personalized learning assistance and roadmap generation
    This is the premium subscription feature
    """
    
    def __init__(self):
        self.llm = get_chat_model()
        self.conversation_history = {}
    
    def get_personalized_response(self, user_id: str, query: str, context: str = None) -> Dict[str, Any]:
        """
        Main method for personalized tutoring responses
        """
        try:
            # Get user context from database
            user_context = parserdb.get_user_context(user_id)
            user_profile = parserdb.get_user_profile(user_id)
            
            # Retrieve conversation history
            history = self.conversation_history.get(user_id, [])
            
            system_prompt = f"""
You are {user_profile.name}'s personal AI tutor on an Egyptian educational social media platform.

STUDENT PROFILE & DATA:
{user_context}

CONVERSATION HISTORY:
{chr(10).join(history[-5:]) if history else "This is the first interaction."}

TUTORING GUIDELINES:
- Address the student by name and reference their specific academic data
- Provide highly personalized advice based on their performance, strengths, and weaknesses
- Consider their target universities ({', '.join(user_profile.target_universities)}) in recommendations
- Adapt to their learning style ({user_profile.learning_style})
- Be encouraging but realistic about their current academic standing
- Suggest specific study techniques, resources, and schedules
- Monitor their progress and celebrate improvements
- Identify areas needing urgent attention
- Provide university-specific preparation advice
- Use a friendly, supportive tone while maintaining academic rigor

RESPONSE REQUIREMENTS:
- Reference specific data points from their profile
- Provide actionable, time-bound recommendations
- Include study schedules when relevant
- Suggest competitive strategies for 1v1 knockouts
- Recommend study groups based on their weak subjects
- End with motivation and next steps
"""
            
            # Generate personalized response
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{query}")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({"query": query})
            
            # Update conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            self.conversation_history[user_id].append(f"Student: {query}")
            self.conversation_history[user_id].append(f"Tutor: {response[:200]}...")
            
            # Keep only last 10 exchanges
            if len(self.conversation_history[user_id]) > 20:
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
            
            return {
                "response": response,
                "user_profile": {
                    "name": user_profile.name,
                    "grade": user_profile.grade_level,
                    "learning_style": user_profile.learning_style
                },
                "recommendations": self._extract_recommendations(response),
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I'm experiencing technical difficulties. Please try again shortly.",
                "error": str(e),
                "success": False
            }
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract actionable recommendations from the response"""
        # Simple keyword-based extraction - can be enhanced with NLP
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'try', 'focus on']):
                recommendations.append(line.strip())
        
        return recommendations[:5]  # Return top 5 recommendations

class KnockoutQuestionGenerator:
    """
    AI Agent for generating 1v1 knockout competition questions
    Ensures fair, grade-appropriate, and engaging questions
    """
    
    def __init__(self):
        self.llm = get_chat_model()
        self.question_cache = {}
    
    def generate_knockout_questions(self, user1_id: str, user2_id: str, subject: str, 
                                  num_questions: int = 10) -> Dict[str, Any]:
        """
        Generate balanced questions for 1v1 knockout competition
        """
        try:
            # Get both users' profiles and performance data
            user1_profile = parserdb.get_user_profile(user1_id)
            user2_profile = parserdb.get_user_profile(user2_id)
            user1_courses = parserdb.get_course_progress(user1_id)
            user2_courses = parserdb.get_course_progress(user2_id)
            
            # Determine appropriate difficulty level
            difficulty = self._calculate_fair_difficulty(user1_courses, user2_courses, subject)
            
            # Generate questions prompt
            generation_prompt = f"""
Generate {num_questions} multiple-choice questions for a 1v1 academic knockout competition between Egyptian students.

COMPETITION DETAILS:
- Subject: {subject}
- Difficulty Level: {difficulty.value}
- Student Grades: {user1_profile.grade_level} vs {user2_profile.grade_level}
- Question Format: Multiple choice with 4 options (A, B, C, D)

REQUIREMENTS:
1. Questions must be curriculum-appropriate for Egyptian education system
2. Balance difficulty to ensure fair competition
3. Include a mix of conceptual and application-based questions
4. Questions should be engaging and competitive
5. Avoid overly complex language
6. Include some visual/spatial questions if applicable
7. Time limit: 30 seconds per question

FORMAT EACH QUESTION AS:
Question [N]: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Letter]
Explanation: [Brief explanation]
Time Limit: 30 seconds
Points: [1-3 based on difficulty]

Ensure questions test different cognitive levels: knowledge, comprehension, application, and analysis.
"""
            
            response = self.llm.invoke([HumanMessage(content=generation_prompt)])
            questions = self._parse_questions(response.content)
            
            # Generate competition metadata
            competition_data = {
                "competition_id": f"knockout_{user1_id}_{user2_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "participants": [user1_id, user2_id],
                "subject": subject,
                "difficulty": difficulty.value,
                "total_questions": len(questions),
                "estimated_duration": len(questions) * 30,  # 30 seconds per question
                "questions": questions,
                "created_at": datetime.now().isoformat(),
                "scoring_system": {
                    "correct_answer": 3,
                    "speed_bonus": 2,
                    "streak_bonus": 1
                }
            }
            
            return {
                "competition_data": competition_data,
                "success": True,
                "balancing_notes": f"Questions balanced for {difficulty.value} level based on participant performance"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "fallback_questions": self._get_fallback_questions(subject)
            }
    
    def _calculate_fair_difficulty(self, user1_courses: List, user2_courses: List, subject: str) -> DifficultyLevel:
        """Calculate appropriate difficulty level for fair competition"""
        # Find subject-specific performance
        user1_performance = 0
        user2_performance = 0
        
        for course in user1_courses:
            if course.subject.lower() == subject.lower():
                user1_performance = course.average_grade
                break
        
        for course in user2_courses:
            if course.subject.lower() == subject.lower():
                user2_performance = course.average_grade
                break
        
        # Calculate average performance
        avg_performance = (user1_performance + user2_performance) / 2
        
        if avg_performance >= 90:
            return DifficultyLevel.EXPERT
        elif avg_performance >= 80:
            return DifficultyLevel.ADVANCED
        elif avg_performance >= 70:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER
    
    def _parse_questions(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse generated questions from LLM response"""
        questions = []
        lines = response_text.split('\n')
        current_question = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Question'):
                if current_question:
                    questions.append(current_question)
                current_question = {"question": line, "options": {}, "metadata": {}}
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                letter = line[0]
                current_question["options"][letter] = line[3:]
            elif line.startswith('Correct Answer:'):
                current_question["correct_answer"] = line.split(':')[1].strip()
            elif line.startswith('Explanation:'):
                current_question["explanation"] = line.split(':', 1)[1].strip()
            elif line.startswith('Points:'):
                current_question["points"] = int(line.split(':')[1].strip())
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _get_fallback_questions(self, subject: str) -> List[Dict[str, Any]]:
        """Provide fallback questions if generation fails"""
        fallback_questions = [
            {
                "question": f"Basic {subject} question for fair competition",
                "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                "correct_answer": "A",
                "explanation": "Fallback question",
                "points": 1
            }
        ]
        return fallback_questions

class ContentModerationAgent:
    """
    AI Agent for moderating educational content (posts, reels, comments)
    Ensures content is educational and appropriate
    """
    
    def __init__(self):
        self.llm = get_chat_model()
        self.moderation_cache = {}
    
    def moderate_content(self, content: str, content_type: ContentType, user_id: str) -> Dict[str, Any]:
        """
        Moderate content for educational appropriateness and safety
        """
        try:
            user_profile = parserdb.get_user_profile(user_id)
            
            moderation_prompt = f"""
Analyze this {content_type.value} content from an Egyptian educational social media platform:

CONTENT TO MODERATE:
"{content}"

USER CONTEXT:
- Grade Level: {user_profile.grade_level}
- School Type: {user_profile.school_type}

MODERATION CRITERIA:
1. Educational Relevance (0-10): Is this content educational or study-related?
2. Age Appropriateness (0-10): Suitable for middle/high school students?
3. Language Appropriateness (0-10): Professional and respectful language?
4. Safety Score (0-10): Free from harmful, bullying, or inappropriate content?
5. Curriculum Alignment (0-10): Aligns with Egyptian education curriculum?

ASSESSMENT REQUIREMENTS:
- Flag content that is not educational
- Identify inappropriate language or behavior
- Check for academic misconduct (cheating, plagiarism hints)
- Ensure cultural sensitivity for Egyptian context
- Verify age-appropriate content

RESPONSE FORMAT:
Educational_Relevance: [score]/10
Age_Appropriateness: [score]/10
Language_Appropriateness: [score]/10
Safety_Score: [score]/10
Curriculum_Alignment: [score]/10
Overall_Score: [average]/10
Decision: [APPROVE/REVIEW/REJECT]
Reasoning: [Brief explanation]
Suggestions: [Improvement suggestions if needed]
Educational_Tags: [Relevant subject tags]
"""
            
            response = self.llm.invoke([HumanMessage(content=moderation_prompt)])
            moderation_result = self._parse_moderation_response(response.content)
            
            # Add metadata
            moderation_result.update({
                "content_type": content_type.value,
                "user_id": user_id,
                "user_grade": user_profile.grade_level,
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content)
            })
            
            return moderation_result
            
        except Exception as e:
            return {
                "decision": "REVIEW",
                "error": str(e),
                "success": False,
                "reasoning": "Error in moderation process, flagging for manual review"
            }
    
    def _parse_moderation_response(self, response: str) -> Dict[str, Any]:
        """Parse moderation response from LLM"""
        result = {"success": True}
        lines = response.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                if 'score' in key:
                    # Extract numeric score
                    score_match = [int(s) for s in value.split() if s.isdigit()]
                    result[key] = score_match[0] if score_match else 5
                elif key == 'decision':
                    result[key] = value.upper()
                elif key in ['reasoning', 'suggestions', 'educational_tags']:
                    result[key] = value
        
        # Calculate overall score if not provided
        if 'overall_score' not in result:
            scores = [result.get(f'{metric}_score', 5) for metric in 
                     ['educational_relevance', 'age_appropriateness', 'language_appropriateness', 'safety', 'curriculum_alignment']]
            result['overall_score'] = sum(scores) / len(scores)
        
        return result

class StudyGroupLocationAgent:
    """
    AI Agent for recommending study group meeting locations
    Uses Egyptian geographic and cultural context
    """
    
    def __init__(self):
        self.llm = get_chat_model()
        self.location_cache = {}
    
    def recommend_study_locations(self, user_ids: List[str], subject: str, 
                                study_duration: int = 2) -> Dict[str, Any]:
        """
        Recommend study group meeting locations based on user profiles and preferences
        """
        try:
            # Get all user profiles
            user_profiles = [parserdb.get_user_profile(uid) for uid in user_ids]
            
            # Get geographic information (mock implementation)
            locations_prompt = f"""
Recommend study group meeting locations for {len(user_profiles)} Egyptian students:

STUDENT GROUP:
"""
            for i, profile in enumerate(user_profiles, 1):
                locations_prompt += f"Student {i}: {profile.grade_level}, {profile.school_type} school\n"
            
            locations_prompt += f"""
STUDY SESSION DETAILS:
- Subject: {subject}
- Expected Duration: {study_duration} hours
- Group Size: {len(user_profiles)} students

LOCATION REQUIREMENTS:
1. Safe and appropriate for students
2. Quiet environment suitable for studying
3. Accessible to all participants
4. Available facilities (tables, wifi, etc.)
5. Cost-effective or free options
6. Cultural appropriateness for Egyptian context

PROVIDE 5 LOCATION RECOMMENDATIONS:
For each location, include:
- Name and type of venue
- Why it's suitable for this study group
- Estimated cost (if any)
- Available facilities
- Best time slots
- Accessibility information
- Safety considerations

Focus on Egyptian locations like:
- Public libraries
- University campuses
- Educational centers
- Community centers
- Cafes with study-friendly environments
- School facilities (if accessible)
"""
            
            response = self.llm.invoke([HumanMessage(content=locations_prompt)])
            recommendations = self._parse_location_recommendations(response.content)
            
            return {
                "recommendations": recommendations,
                "group_size": len(user_profiles),
                "subject": subject,
                "duration": study_duration,
                "success": True,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "fallback_recommendations": self._get_fallback_locations()
            }
    
    def _parse_location_recommendations(self, response: str) -> List[Dict[str, Any]]:
        """Parse location recommendations from LLM response"""
        recommendations = []
        current_location = {}
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('-') and ':' not in line and current_location:
                recommendations.append(current_location)
                current_location = {"name": line}
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                current_location[key] = value.strip()
        
        if current_location:
            recommendations.append(current_location)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _get_fallback_locations(self) -> List[Dict[str, Any]]:
        """Provide fallback location recommendations"""
        return [
            {
                "name": "Local Public Library",
                "type": "Library",
                "cost": "Free",
                "facilities": "Tables, chairs, WiFi, quiet environment",
                "safety": "High"
            },
            {
                "name": "University Campus Study Area",
                "type": "Educational Institution",
                "cost": "Free",
                "facilities": "Study rooms, WiFi, academic atmosphere",
                "safety": "High"
            }
        ]

# AI Agents Manager
class AIAgentsManager:
    """
    Central manager for all AI agents
    """
    
    def __init__(self):
        self.personal_tutor = PersonalTutorAgent()
        self.knockout_generator = KnockoutQuestionGenerator()
        self.content_moderator = ContentModerationAgent()
        self.location_agent = StudyGroupLocationAgent()
        
        # Track agent usage for billing (subscription feature)
        self.usage_tracker = {}
    
    def get_agent(self, agent_type: AgentType):
        """Get specific agent instance"""
        agents = {
            AgentType.PERSONAL_TUTOR: self.personal_tutor,
            AgentType.KNOCKOUT_GENERATOR: self.knockout_generator,
            AgentType.CONTENT_MODERATOR: self.content_moderator,
            AgentType.LOCATION_RECOMMENDER: self.location_agent
        }
        return agents.get(agent_type)
    
    def track_usage(self, user_id: str, agent_type: AgentType):
        """Track agent usage for subscription billing"""
        if user_id not in self.usage_tracker:
            self.usage_tracker[user_id] = {}
        
        if agent_type not in self.usage_tracker[user_id]:
            self.usage_tracker[user_id][agent_type] = 0
        
        self.usage_tracker[user_id][agent_type] += 1
    
    def check_subscription_limits(self, user_id: str, agent_type: AgentType) -> bool:
        """Check if user has exceeded subscription limits"""
        # Mock implementation - integrate with your subscription system
        if agent_type == AgentType.PERSONAL_TUTOR:
            # Personal tutor is premium feature
            daily_limit = 10  # 10 interactions per day for premium users
            usage_today = self.usage_tracker.get(user_id, {}).get(agent_type, 0)
            return usage_today < daily_limit
        
        return True  # Other features are free

# Global manager instance
ai_agents = AIAgentsManager()

