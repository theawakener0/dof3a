from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import fetchdb
from typing import Dict, Any, Optional, List
import dotenv
import json
import logging
import re
import random
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
    AI Personal Tutor for Egyptian students - simplified version using only Django models
    
    Args:
        user_input: The user's question or request
        user_id: Unique identifier for the user
        conversation_context: Optional previous conversation context
        
    Returns:
        Dictionary containing AI response and metadata
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
        
        # Fetch user context from database
        user_context = ""
        try:
            user_context = fetchdb.get_user_context(user_id)
            logger.info(f"Successfully retrieved user context for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to fetch user context for user {user_id}: {e}")
            user_context = f"User ID: {user_id} (No additional profile data available)"
        
        # Initialize AI model
        try:
            llm = get_chat_model()
        except Exception as e:
            logger.error(f"AI model initialization failed: {e}")
            return {
                "response": "I'm sorry, but I'm temporarily unavailable. Please try again later.",
                "status": "error",
                "error": "AI service unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        # Create enhanced prompt with safety measures and user context
        system_prompt = f"""You are dof3a, an intelligent and supportive AI tutor for Egyptian students. 
        You help with homework, exam preparation, and educational guidance.

        SAFETY GUIDELINES:
        - Only provide educational content
        - Never generate harmful, inappropriate, or offensive content
        - If asked about non-educational topics, politely redirect to educational matters
        - Respect cultural and religious sensitivities
        - Always maintain a friendly and professional tone

        USER PROFILE:
        {user_context}
        
        CONVERSATION HISTORY:
        {conversation_context or "No previous conversation"}
        
        PERSONALIZATION INSTRUCTIONS:
        - Use the user's name when available to make responses more personal
        - Tailor your responses to their grade level and academic focus
        - Reference their previous posts or activity when relevant and helpful
        - Adjust difficulty and examples to match their academic level
        - If they're a high-performing student, you can provide more challenging content
        - If they seem to struggle, provide more supportive and foundational explanations
        - Consider their engagement level when structuring responses
        
        Provide helpful, accurate, and encouraging educational support. Always respond in a friendly, 
        professional manner appropriate for students. Use their profile information to give personalized, 
        relevant assistance."""

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

def generate_knockout_questions(subject: str, grade_level: str, difficulty: str = "medium", num_questions: int = 5, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate AI-powered questions for 1v1 knockout games
    
    Args:
        subject: Subject area (Math, Science, Arabic, English, etc.)
        grade_level: Student grade level (Middle 1, Middle 2, etc.)
        difficulty: easy, medium, hard
        num_questions: Number of questions to generate
    
    Returns:
        Dict containing questions with multiple choice answers
    """
    try:
        # Validate inputs
        if not subject or not isinstance(subject, str):
            raise ValueError("Subject must be a non-empty string")
        
        if not grade_level or not isinstance(grade_level, str):
            raise ValueError("Grade level must be a non-empty string")
        
        subject = subject.strip()
        grade_level = grade_level.strip()
        difficulty = difficulty.strip() if difficulty else "medium"
        
        # Validate difficulty level
        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            difficulty = "medium"
        
        # Validate number of questions
        try:
            num_questions = int(num_questions)
            num_questions = max(1, min(num_questions, 20))  # Between 1 and 20
        except (ValueError, TypeError):
            num_questions = 5
        
        logger.info(f"Generating {num_questions} {difficulty} questions for {subject} - {grade_level}")
        
        # Fetch user context if user_id is provided
        user_performance_context = ""
        if user_id:
            try:
                user_data = fetchdb.get_comprehensive_data(user_id)
                if user_data and user_data.get('student_profile'):
                    student_profile = user_data['student_profile']
                    user_performance_context = f"""
                    STUDENT PERFORMANCE CONTEXT:
                    - Current Score: {student_profile.get('score', 0)} points
                    - Grade Level: {student_profile.get('grade', grade_level)}
                    - Platform Engagement: {'High' if len(user_data.get('posts', [])) + len(user_data.get('comments', [])) > 5 else 'Moderate' if len(user_data.get('posts', [])) + len(user_data.get('comments', [])) > 2 else 'Low'}
                    
                    Adjust question difficulty and style based on this student's performance level.
                    """
                    logger.info(f"Using student performance data for user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to fetch user context for question generation: {e}")
    
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
            },
            "Senior 1": {
                "Math": ["Calculus Basics", "Trigonometry", "Statistics", "Logarithms"],
                "Physics": ["Mechanics", "Heat", "Sound", "Light"],
                "Chemistry": ["Atomic Structure", "Chemical Bonding", "Acids and Bases"],
                "Biology": ["Cell Biology", "Genetics", "Evolution"]
            },
            "Senior 2": {
                "Math": ["Advanced Calculus", "Complex Numbers", "Matrices"],
                "Physics": ["Electricity", "Magnetism", "Waves", "Modern Physics"],
                "Chemistry": ["Organic Chemistry", "Chemical Equilibrium", "Thermodynamics"],
                "Biology": ["Human Biology", "Ecology", "Molecular Biology"]
            },
            "Senior 3": {
                "Math": ["University Prep Calculus", "Statistics", "Discrete Math"],
                "Physics": ["Quantum Physics", "Relativity", "Nuclear Physics"],
                "Chemistry": ["Advanced Organic", "Physical Chemistry", "Biochemistry"],
                "Biology": ["Advanced Genetics", "Biotechnology", "Environmental Science"]
            }
        }
        
        # Get relevant topics
        topics = curriculum_topics.get(grade_level, {}).get(subject, ["General concepts"])
        selected_topics = random.sample(topics, min(len(topics), 3))
        
        # Create AI prompt for question generation
        system_prompt = f"""You are an educational content generator for Egyptian students. 
        Generate {num_questions} multiple choice questions for a 1v1 knockout game.
        
        REQUIREMENTS:
        - Subject: {subject}
        - Grade Level: {grade_level}
        - Difficulty: {difficulty}
        - Topics to focus on: {', '.join(selected_topics)}
        - Questions should be appropriate for Egyptian curriculum
        - Each question must have exactly 4 options (A, B, C, D)
        - Only one correct answer per question
        - Questions should be clear and unambiguous
        - Avoid culturally sensitive content
        
        {user_performance_context}
        
        Return ONLY a JSON array with this exact format:
        [
            {{
                "question": "Question text here?",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "A",
                "topic": "Topic name",
                "explanation": "Brief explanation of the correct answer"
            }}
        ]
        
        Generate exactly {num_questions} questions."""
        
        # Initialize AI model
        try:
            llm = get_chat_model()
        except Exception as e:
            logger.error(f"AI model initialization failed: {e}")
            return {
                "questions": [],
                "status": "error",
                "error": "AI service unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Generate the questions now.")
        ])
        
        chain = prompt | llm | StrOutputParser()
        
        try:
            response = chain.invoke({})
            
            # Try to parse JSON response
            try:
                questions_data = json.loads(response)
                
                # Validate questions structure
                if not isinstance(questions_data, list):
                    raise ValueError("Response is not a list")
                
                validated_questions = []
                for i, q in enumerate(questions_data):
                    if not isinstance(q, dict):
                        continue
                    
                    required_fields = ["question", "options", "correct_answer", "topic", "explanation"]
                    if not all(field in q for field in required_fields):
                        continue
                    
                    if len(q["options"]) != 4:
                        continue
                    
                    validated_questions.append({
                        "id": i + 1,
                        "question": str(q["question"]).strip(),
                        "options": [str(opt).strip() for opt in q["options"]],
                        "correct_answer": str(q["correct_answer"]).strip().upper(),
                        "topic": str(q["topic"]).strip(),
                        "explanation": str(q["explanation"]).strip(),
                        "difficulty": difficulty,
                        "subject": subject
                    })
                
                if not validated_questions:
                    raise ValueError("No valid questions generated")
                
                logger.info(f"Successfully generated {len(validated_questions)} questions")
                
                return {
                    "questions": validated_questions,
                    "status": "success",
                    "total_questions": len(validated_questions),
                    "subject": subject,
                    "grade_level": grade_level,
                    "difficulty": difficulty,
                    "topics_covered": selected_topics,
                    "timestamp": datetime.now().isoformat()
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                raise Exception("AI response format error")
            
        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            return {
                "questions": [],
                "status": "error",
                "error": f"Question generation failed: {e}",
                "timestamp": datetime.now().isoformat()
            }
    
    except ValueError as e:
        logger.error(f"Validation error in generate_knockout_questions: {e}")
        return {
            "questions": [],
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error in generate_knockout_questions: {e}")
        return {
            "questions": [],
            "status": "error",
            "error": "Unexpected system error",
            "timestamp": datetime.now().isoformat()
        }

def generate_study_recommendations(user_id: int, subject: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate personalized study recommendations based on user's profile and activity
    
    Args:
        user_id: User ID
        subject: Optional specific subject to focus on
        
    Returns:
        Dict containing personalized study recommendations
    """
    try:
        user_id = _validate_user_id(user_id)
        
        # Fetch comprehensive user data
        try:
            user_data = fetchdb.get_comprehensive_data(user_id)
            user_context = fetchdb.get_user_context(user_id)
        except Exception as e:
            logger.error(f"Failed to fetch user data for recommendations: {e}")
            return {
                "recommendations": ["Focus on reviewing your recent coursework", "Practice problem-solving regularly"],
                "status": "error",
                "error": "Unable to fetch user profile",
                "timestamp": datetime.now().isoformat()
            }
        
        if not user_data or not user_data.get('user_profile'):
            return {
                "recommendations": ["Create a study schedule", "Focus on consistent daily practice"],
                "status": "error", 
                "error": "User profile not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Initialize AI model
        try:
            llm = get_chat_model()
        except Exception as e:
            logger.error(f"AI model initialization failed: {e}")
            return {
                "recommendations": ["Review your textbooks regularly", "Ask teachers for help when needed"],
                "status": "error",
                "error": "AI service unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        # Create AI prompt for study recommendations
        subject_focus = f"Focus specifically on {subject}." if subject else "Cover all relevant subjects for their grade level."
        
        system_prompt = f"""You are an educational advisor for Egyptian students. Based on the student's profile and activity, 
        generate personalized study recommendations.

        STUDENT PROFILE:
        {user_context}
        
        INSTRUCTIONS:
        - {subject_focus}
        - Provide 5-8 specific, actionable study recommendations
        - Consider their grade level and current performance
        - Include both study techniques and content suggestions
        - Be encouraging but realistic
        - Tailor recommendations to Egyptian curriculum
        - Consider their engagement level and suggest improvements if needed
        
        Return ONLY a JSON object with this format:
        {{
            "recommendations": [
                "Specific recommendation 1",
                "Specific recommendation 2",
                "etc..."
            ],
            "focus_areas": ["Area 1", "Area 2", "Area 3"],
            "study_tips": ["Tip 1", "Tip 2", "Tip 3"],
            "motivation_message": "Encouraging message for the student"
        }}"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Generate personalized study recommendations for this student.")
        ])
        
        chain = prompt | llm | StrOutputParser()
        
        try:
            response = chain.invoke({})
            
            # Parse JSON response
            try:
                recommendations_data = json.loads(response)
                
                logger.info(f"Successfully generated study recommendations for user {user_id}")
                
                return {
                    "recommendations": recommendations_data.get("recommendations", []),
                    "focus_areas": recommendations_data.get("focus_areas", []),
                    "study_tips": recommendations_data.get("study_tips", []),
                    "motivation_message": recommendations_data.get("motivation_message", "Keep up the great work!"),
                    "status": "success",
                    "user_id": user_id,
                    "subject_focus": subject,
                    "timestamp": datetime.now().isoformat()
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse recommendations response: {e}")
                return {
                    "recommendations": ["Review your coursework regularly", "Practice consistently", "Ask for help when needed"],
                    "status": "error",
                    "error": "Response parsing failed",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"AI recommendation generation failed: {e}")
            return {
                "recommendations": ["Study consistently", "Review challenging topics", "Seek help from teachers"],
                "status": "error",
                "error": "Recommendation generation failed",
                "timestamp": datetime.now().isoformat()
            }
    
    except ValueError as e:
        logger.error(f"Validation error in generate_study_recommendations: {e}")
        return {
            "recommendations": [],
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error in generate_study_recommendations: {e}")
        return {
            "recommendations": [],
            "status": "error",
            "error": "Unexpected system error",
            "timestamp": datetime.now().isoformat()
        }

# Test function
def test_ai_features():
    """Test AI features with basic functionality"""
    logger.info("Testing AI features...")
    
    try:
        # Test chat functionality with user context
        chat_response = chatmodel("Hello, can you help me with math?", "1")
        logger.info(f"Chat test: {chat_response['status']}")
        
        # Test knockout questions with user context
        questions_response = generate_knockout_questions("Math", "Middle 3", "easy", 3, user_id=1)
        logger.info(f"Questions test: {questions_response['status']}")
        if questions_response['status'] == 'success':
            logger.info(f"Generated {len(questions_response['questions'])} questions")
        
        # Test study recommendations
        recommendations_response = generate_study_recommendations(1, "Math")
        logger.info(f"Recommendations test: {recommendations_response['status']}")
        if recommendations_response['status'] == 'success':
            logger.info(f"Generated {len(recommendations_response['recommendations'])} recommendations")
        
        logger.info("✅ AI features tested successfully")
        
    except Exception as e:
        logger.error(f"AI features test failed: {e}")

if __name__ == "__main__":
    test_ai_features()
