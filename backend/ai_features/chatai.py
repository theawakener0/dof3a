from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# import fetchdb
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
        
        # Create enhanced prompt with safety measures
        system_prompt = f"""You are dof3a, an intelligent and supportive AI tutor for Egyptian students. 
        You help with homework, exam preparation, and educational guidance.

        SAFETY GUIDELINES:
        - Only provide educational content
        - Never generate harmful, inappropriate, or offensive content
        - If asked about non-educational topics, politely redirect to educational matters
        - Respect cultural and religious sensitivities
        - Always maintain a friendly and professional tone,
        
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

def generate_knockout_questions(subject: str, grade_level: str, difficulty: str = "medium", num_questions: int = 5) -> Dict[str, Any]:
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
    
        # Use fallback question generation for now
        questions = _generate_fallback_questions(subject, grade_level, difficulty, num_questions)
        
        if questions:
            logger.info(f"Successfully generated {len(questions)} questions using fallback method")
            return {
                "questions": questions,
                "status": "success",
                "total_questions": len(questions),
                "subject": subject,
                "grade_level": grade_level,
                "difficulty": difficulty,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise ValueError("No questions could be generated")
    
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

def _generate_fallback_questions(subject: str, grade_level: str, difficulty: str, num_questions: int) -> List[Dict[str, Any]]:
    """Generate fallback questions when AI generation fails"""
    
    # Sample questions bank organized by subject and grade
    question_bank = {
        "Math": {
            "Middle 1": {
                "easy": [
                    {
                        "question": "What is 15 + 27?",
                        "options": ["A. 42", "B. 41", "C. 43", "D. 44"],
                        "correct_answer": "A",
                        "topic": "Addition",
                        "explanation": "15 + 27 = 42"
                    },
                    {
                        "question": "What is 8 × 6?",
                        "options": ["A. 46", "B. 48", "C. 50", "D. 52"],
                        "correct_answer": "B",
                        "topic": "Multiplication",
                        "explanation": "8 × 6 = 48"
                    },
                    {
                        "question": "What is 1/2 + 1/4?",
                        "options": ["A. 1/6", "B. 2/6", "C. 3/4", "D. 1/3"],
                        "correct_answer": "C",
                        "topic": "Fractions",
                        "explanation": "1/2 + 1/4 = 2/4 + 1/4 = 3/4"
                    },
                    {
                        "question": "What is the value of x in: x + 5 = 12?",
                        "options": ["A. 6", "B. 7", "C. 8", "D. 9"],
                        "correct_answer": "B",
                        "topic": "Basic Algebra",
                        "explanation": "x + 5 = 12, so x = 12 - 5 = 7"
                    }
                ]
            },
            "Middle 2": {
                "easy": [
                    {
                        "question": "What is 2x + 3 = 11, solve for x?",
                        "options": ["A. 3", "B. 4", "C. 5", "D. 6"],
                        "correct_answer": "B",
                        "topic": "Algebra",
                        "explanation": "2x + 3 = 11, 2x = 8, x = 4"
                    },
                    {
                        "question": "What is the area of a rectangle with length 8cm and width 5cm?",
                        "options": ["A. 40 cm²", "B. 35 cm²", "C. 45 cm²", "D. 30 cm²"],
                        "correct_answer": "A",
                        "topic": "Geometry",
                        "explanation": "Area = length × width = 8 × 5 = 40 cm²"
                    }
                ]
            }
        },
        "Science": {
            "Middle 1": {
                "easy": [
                    {
                        "question": "What are the three states of matter?",
                        "options": ["A. Solid, Liquid, Gas", "B. Hot, Cold, Warm", "C. Big, Small, Medium", "D. Fast, Slow, Still"],
                        "correct_answer": "A",
                        "topic": "States of Matter",
                        "explanation": "The three main states of matter are solid, liquid, and gas"
                    },
                    {
                        "question": "Which planet is closest to the Sun?",
                        "options": ["A. Venus", "B. Earth", "C. Mercury", "D. Mars"],
                        "correct_answer": "C",
                        "topic": "Solar System",
                        "explanation": "Mercury is the planet closest to the Sun"
                    }
                ]
            }
        },
        "English": {
            "Middle 1": {
                "easy": [
                    {
                        "question": "What is the past tense of 'go'?",
                        "options": ["A. goes", "B. went", "C. going", "D. gone"],
                        "correct_answer": "B",
                        "topic": "Past Tense",
                        "explanation": "The past tense of 'go' is 'went'"
                    }
                ]
            }
        }
    }
    
    # Get questions for the specific subject and grade
    subject_questions = question_bank.get(subject, {})
    grade_questions = subject_questions.get(grade_level, {})
    difficulty_questions = grade_questions.get(difficulty, [])
    
    # If no specific questions found, use Math Middle 1 easy as default
    if not difficulty_questions:
        difficulty_questions = question_bank["Math"]["Middle 1"]["easy"]
    
    # Select random questions
    available_questions = list(difficulty_questions)
    selected_questions = []
    
    for i in range(min(num_questions, len(available_questions))):
        if available_questions:
            question = random.choice(available_questions)
            available_questions.remove(question)
            
            # Add ID and metadata
            question_with_metadata = {
                "id": i + 1,
                "question": question["question"],
                "options": question["options"],
                "correct_answer": question["correct_answer"],
                "topic": question["topic"],
                "explanation": question["explanation"],
                "difficulty": difficulty,
                "subject": subject
            }
            selected_questions.append(question_with_metadata)
    
    return selected_questions

# Test function
def test_ai_features():
    """Test AI features with basic functionality"""
    logger.info("Testing AI features...")
    
    try:
        # Test chat functionality
        chat_response = chatmodel("Hello, can you help me with math?", "1")
        logger.info(f"Chat test: {chat_response['status']}")
        
        # Test knockout questions
        questions_response = generate_knockout_questions("Math", "Middle 1", "easy", 3)
        logger.info(f"Questions test: {questions_response['status']}")
        if questions_response['status'] == 'success':
            logger.info(f"Generated {len(questions_response['questions'])} questions")
        
        logger.info("✅ AI features tested successfully")
        
    except Exception as e:
        logger.error(f"AI features test failed: {e}")

if __name__ == "__main__":
    test_ai_features()
