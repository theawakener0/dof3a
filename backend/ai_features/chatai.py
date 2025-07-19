from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
import fetchdb
from typing import Dict, Any, Optional, List
import dotenv
import json
import random
import logging
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()
API_KEY = dotenv.get_key(".env", "GOOGLE_API_KEY") or "AIzaSyBaehWDyGXoFCqVexZxAov9DAGJvpWa5kQ"

def _validate_api_key() -> bool:
    """Validate Google API key is available"""
    if not API_KEY or API_KEY.strip() == "" or API_KEY == "demo_key_for_testing":
        logger.warning("Google API key not configured")
        return False
    return True

def _sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potentially harmful patterns
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Limit length to prevent excessive processing
    if len(text) > 5000:
        logger.warning(f"Input text truncated from {len(text)} to 5000 characters")
        text = text[:5000] + "..."
    
    return text.strip()

def _validate_user_id(user_id: Any) -> int:
    """Validate and convert user_id to integer"""
    if user_id is None:
        raise ValueError("User ID cannot be None")
    
    try:
        user_id = int(user_id)
        if user_id <= 0:
            raise ValueError("User ID must be a positive integer")
        return user_id
    except (ValueError, TypeError):
        raise ValueError(f"Invalid user ID: {user_id}. Must be a positive integer.")

def get_chat_model():
    """Initialize and return the GoogleGenerativeAI model with validation"""
    try:
        if not _validate_api_key():
            raise ValueError("Google API key is not configured properly")
        
        return GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=API_KEY,
            temperature=0.5
        )
    except Exception as e:
        logger.error(f"Failed to initialize chat model: {e}")
        raise Exception(f"AI model initialization failed: {e}")

def chatmodel(user_input: str, user_id: str, conversation_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Enhanced AI Personal Tutor with comprehensive user context integration and validation
    
    Args:
        user_input: The user's question or request
        user_id: Unique identifier for the user
        conversation_context: Optional previous conversation context
        
    Returns:
        Dictionary containing AI response and metadata
        
    Raises:
        ValueError: If inputs are invalid
        Exception: If AI processing fails
    """
    try:
        # Validate and sanitize inputs
        if not user_input or not isinstance(user_input, str):
            raise ValueError("User input must be a non-empty string")
        
        user_input = _sanitize_input(user_input)
        if not user_input:
            raise ValueError("User input is empty after sanitization")
        
        user_id = _validate_user_id(user_id)
        
        # Sanitize conversation context if provided
        if conversation_context:
            conversation_context = _sanitize_input(conversation_context)
        
        logger.info(f"Processing chat request for user {user_id}")
        
        # Get user context with error handling
        try:
            user_context = fetchdb.get_user_context(user_id)
            if not user_context:
                logger.warning(f"No user context found for user {user_id}, using default")
                user_context = "No user profile found."
        except Exception as e:
            logger.warning(f"Failed to fetch user context for user {user_id}: {e}")
            user_context = "User profile temporarily unavailable."
        
        # Initialize AI model
        try:
            llm = get_chat_model()
        except Exception as e:
            logger.error(f"AI model initialization failed: {e}")
            return {
                "response": "I'm sorry, but I'm temporarily unavailable. Please try again later.",
                "status": "error",
                "error": "AI service unavailable"
            }
        
        # Create enhanced prompt with safety measures
        system_prompt = f"""You are dof3a an intelligent and supportive AI tutor for Egyptian students. 
        You help with homework, exam preparation, and educational guidance.

        SAFETY GUIDELINES:
        - Only provide educational content
        - Never generate harmful, inappropriate, or offensive content
        - If asked about non-educational topics, politely redirect to educational matters
        - Respect cultural and religious sensitivities
        
        CURRENT USER CONTEXT:
        {user_context}
        
        CONVERSATION HISTORY:
        {conversation_context or "No previous conversation"}
        
        Provide helpful, accurate, and encouraging educational support. Always respond in a friendly, 
        professional manner appropriate for students."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        # Create processing chain
        chain = prompt | llm | StrOutputParser()
        
        # Process with timeout and error handling
        try:
            response = chain.invoke({"input": user_input})
            
            if not response or len(response.strip()) == 0:
                raise Exception("AI model returned empty response")
            
            # Validate response length
            if len(response) > 4000:
                logger.warning("AI response was very long, truncating")
                response = response[:4000] + "..."
            
            logger.info(f"Successfully processed chat request for user {user_id}")
            
            return {
                "response": response,
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "input_length": len(user_input),
                "response_length": len(response)
            }
            
        except Exception as e:
            logger.error(f"AI processing failed for user {user_id}: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try rephrasing your question or try again later.",
                "status": "error",
                "error": f"Processing failed: {str(e)[:100]}",
                "timestamp": datetime.now().isoformat()
            }
    
    except ValueError as e:
        logger.error(f"Validation error in chatmodel: {e}")
        return {
            "response": "I'm sorry, but there was an issue with your request. Please check your input and try again.",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error in chatmodel: {e}")
        return {
            "response": "I'm experiencing technical difficulties. Please try again later.",
            "status": "error",
            "error": "Unexpected system error",
            "timestamp": datetime.now().isoformat()
        }

def generate_knockout_questions(subject: str, grade_level: str, difficulty: str = "medium", num_questions: int = 10) -> Dict[str, Any]:
    """
    Generate AI-powered questions for 1v1 knockout games with comprehensive validation
    
    Args:
        subject: Subject area (Math, Science, Arabic, English, etc.)
        grade_level: Student grade level
        difficulty: easy, medium, hard
        num_questions: Number of questions to generate
    
    Returns:
        Dict containing questions with multiple choice answers
        
    Raises:
        ValueError: If inputs are invalid
        Exception: If AI generation fails
    """
    try:
        # Validate inputs
        if not subject or not isinstance(subject, str):
            raise ValueError("Subject must be a non-empty string")
        
        if not grade_level or not isinstance(grade_level, str):
            raise ValueError("Grade level must be a non-empty string")
        
        subject = _sanitize_input(subject)
        grade_level = _sanitize_input(grade_level)
        difficulty = _sanitize_input(difficulty) if difficulty else "medium"
        
        # Validate difficulty level
        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            logger.warning(f"Invalid difficulty '{difficulty}', using 'medium'")
            difficulty = "medium"
        
        # Validate number of questions
        try:
            num_questions = int(num_questions)
            if num_questions <= 0 or num_questions > 50:
                raise ValueError("Number of questions must be between 1 and 50")
        except (ValueError, TypeError):
            raise ValueError("Number of questions must be a valid integer")
        
        logger.info(f"Generating {num_questions} {difficulty} questions for {subject} - {grade_level}")
    
        # Define Egyptian curriculum-specific topics
        curriculum_topics = {
            "Middle 1": {
                "Math": ["Integers", "Fractions", "Decimals", "Basic Algebra", "Geometry Basics"],
                "Science": ["Matter States", "Simple Machines", "Plant Biology", "Solar System"],
                "Arabic": ["Grammar Basics", "Reading Comprehension", "Poetry", "Composition"],
                "English": ["Present Tense", "Vocabulary", "Reading", "Basic Writing"]
            },
            "Middle 2": {
                "Math": ["Algebra", "Geometry", "Statistics", "Equations", "Functions"],
                "Science": ["Chemistry Basics", "Physics Introduction", "Biology Systems"],
                "Arabic": ["Advanced Grammar", "Literature", "Writing Skills"],
                "English": ["Past Tenses", "Conditionals", "Advanced Vocabulary"]
            },
            "Middle 3": {
                "Math": ["Advanced Algebra", "Geometry", "Probability", "Functions"],
                "Science": ["Chemical Reactions", "Forces and Motion", "Genetics Basics"],
                "Arabic": ["Poetry Analysis", "Essay Writing", "Classical Literature"],
                "English": ["Complex Grammar", "Academic Writing", "Literature Analysis"]
            }
        }
        
        # Get relevant topics
        topics = curriculum_topics.get(grade_level, {}).get(subject, ["General concepts"])
        
        # Create AI prompt for question generation
        prompt = f"""
        Generate {num_questions} multiple-choice questions for Egyptian {grade_level} students studying {subject}.
        
        REQUIREMENTS:
        - Difficulty level: {difficulty}
        - Topics to cover: {', '.join(topics)}
        - Each question should have 4 options (A, B, C, D)
        - Mark the correct answer clearly
        - Use culturally appropriate examples and contexts
        - Follow Egyptian curriculum standards
        
        FORMAT RESPONSE AS JSON:
        {{
            "questions": [
                {{
                    "id": 1,
                    "question": "Question text here",
                    "options": {{
                        "A": "Option A",
                        "B": "Option B", 
                        "C": "Option C",
                        "D": "Option D"
                    }},
                    "correct_answer": "A",
                    "explanation": "Why this answer is correct",
                    "topic": "Specific topic covered",
                    "difficulty": "{difficulty}"
                }}
            ]
        }}
        """
        
        try:
            llm = get_chat_model()
            response = llm.invoke(prompt)
            
            # Try to parse JSON response
            try:
                questions_data = json.loads(response)
                
                # Validate the structure
                if "questions" not in questions_data:
                    raise ValueError("Response missing 'questions' field")
                
                questions = questions_data["questions"]
                if len(questions) != num_questions:
                    logger.warning(f"Generated {len(questions)} questions instead of {num_questions}")
                
                # Validate each question
                for i, q in enumerate(questions):
                    required_fields = ["question", "options", "correct_answer", "explanation"]
                    for field in required_fields:
                        if field not in q:
                            raise ValueError(f"Question {i+1} missing required field: {field}")
                
                logger.info(f"Successfully generated {len(questions)} knockout questions")
                
                return {
                    "status": "success",
                    "questions": questions,
                    "subject": subject,
                    "grade_level": grade_level,
                    "difficulty": difficulty,
                    "count": len(questions),
                    "timestamp": datetime.now().isoformat()
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                raise Exception("AI response format error")
                
        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            raise Exception(f"Question generation failed: {e}")
    
    except ValueError as e:
        logger.error(f"Validation error in generate_knockout_questions: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error in generate_knockout_questions: {e}")
        return {
            "status": "error", 
            "error": "Question generation service temporarily unavailable",
            "timestamp": datetime.now().isoformat()
        }

def get_study_roadmap(user_id: int, subject: str, target_grade: str = None) -> Dict[str, Any]:
    """
    Generate personalized study roadmap with comprehensive validation
    
    Args:
        user_id: User ID
        subject: Subject for the roadmap
        target_grade: Optional target grade level
        
    Returns:
        Dict containing personalized study roadmap
        
    Raises:
        ValueError: If inputs are invalid
        Exception: If roadmap generation fails
    """
    try:
        # Validate inputs
        user_id = _validate_user_id(user_id)
        
        if not subject or not isinstance(subject, str):
            raise ValueError("Subject must be a non-empty string")
        
        subject = _sanitize_input(subject)
        if target_grade:
            target_grade = _sanitize_input(target_grade)
        
        logger.info(f"Generating study roadmap for user {user_id} - {subject}")
        
        # Get user data with error handling
        try:
            user_profile = fetchdb.get_user_profile(user_id)
            analytics = fetchdb.get_learning_analytics(user_id)
            course_progress = fetchdb.get_course_progress(user_id)
        except Exception as e:
            logger.warning(f"Failed to fetch user data for roadmap: {e}")
            user_profile = None
            analytics = None
            course_progress = []
        
        current_grade = user_profile.grade if user_profile else "Middle 1"
        
        # Create roadmap prompt
        user_context = f"""
        Current Grade: {current_grade}
        Target Grade: {target_grade or "Next level"}
        Subject: {subject}
        
        Performance Data:
        - Total Points: {analytics.total_points if analytics else 0}
        - Win Rate: {analytics.win_rate if analytics else 0}%
        - Current Streak: {analytics.current_streak if analytics else 0} days
        - Study Sessions: {analytics.total_sessions if analytics else 0}
        
        Progress in {subject}: {len([cp for cp in course_progress if subject.lower() in cp.subject.lower()])} completed units
        """
        
        prompt = f"""
        Create a personalized 4-week study roadmap for an Egyptian student studying {subject}.
        
        STUDENT CONTEXT:
        {user_context}
        
        Create a roadmap with:
        1. Weekly goals and milestones
        2. Daily study tasks (30-45 minutes each)
        3. Practice exercises and review sessions
        4. Assessment checkpoints
        5. Motivational milestones
        
        FORMAT AS JSON:
        {{
            "roadmap": {{
                "subject": "{subject}",
                "duration": "4 weeks",
                "weekly_goals": [
                    {{
                        "week": 1,
                        "goal": "Week goal description",
                        "daily_tasks": [
                            "Day 1: Task description",
                            "Day 2: Task description",
                            ...
                        ],
                        "checkpoint": "Assessment or review activity"
                    }}
                ],
                "resources": ["List of recommended resources"],
                "success_metrics": ["How to measure progress"]
            }}
        }}
        """
        
        try:
            llm = get_chat_model()
            response = llm.invoke(prompt)
            
            # Parse JSON response
            try:
                roadmap_data = json.loads(response)
                
                if "roadmap" not in roadmap_data:
                    raise ValueError("Response missing 'roadmap' field")
                
                logger.info(f"Successfully generated study roadmap for user {user_id}")
                
                return {
                    "status": "success",
                    "roadmap": roadmap_data["roadmap"],
                    "user_id": user_id,
                    "subject": subject,
                    "timestamp": datetime.now().isoformat()
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse roadmap response as JSON: {e}")
                raise Exception("Roadmap response format error")
                
        except Exception as e:
            logger.error(f"AI roadmap generation failed: {e}")
            raise Exception(f"Roadmap generation failed: {e}")
    
    except ValueError as e:
        logger.error(f"Validation error in get_study_roadmap: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_study_roadmap: {e}")
        return {
            "status": "error",
            "error": "Study roadmap service temporarily unavailable", 
            "timestamp": datetime.now().isoformat()
        }

# Test function with comprehensive error handling
def test_ai_features():
    """Test all AI features with error handling"""
    logger.info("Testing AI features...")
    
    try:
        # Test chat model
        chat_result = chatmodel("What is 2+2?", "1")
        logger.info(f"Chat test: {chat_result.get('status', 'unknown')}")
        
        # Test question generation
        questions_result = generate_knockout_questions("Math", "Middle 1", "easy", 3)
        logger.info(f"Questions test: {questions_result.get('status', 'unknown')}")
        
        # Test roadmap generation
        roadmap_result = get_study_roadmap(1, "Math")
        logger.info(f"Roadmap test: {roadmap_result.get('status', 'unknown')}")
        
        logger.info("✅ All AI features tested successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ AI features test failed: {e}")
        return False

if __name__ == "__main__":
    test_ai_features()
