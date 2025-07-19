from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
import parserdb
from typing import Dict, Any, Optional

def get_chat_model():
    """Initialize and return the ChatVertexAI model"""
    return ChatVertexAI(
        model="gemini-1.5-flash-001",
        temperature=0.7,
        max_tokens=2048,
        top_p=0.8
    )

def chatmodel(user_input: str, user_id: str, conversation_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Enhanced chat model with full user context integration
    
    Args:
        user_input: The user's question or request
        user_id: Unique identifier for the user
        conversation_context: Previous conversation context (optional)
    
    Returns:
        Dict containing AI response and additional metadata
    """
    
    # Get comprehensive user data from database
    try:
        user_context = parserdb.get_user_context(user_id)
        user_profile = parserdb.get_user_profile(user_id)
    except Exception as e:
        return {
            "response": "I'm sorry, I couldn't access your profile data at the moment. Please try again later.",
            "error": str(e),
            "success": False
        }

    # Enhanced system prompt with comprehensive user awareness
    system_prompt = f"""
You are an AI specialized personal tutor and academic advisor for Egyptian students (Middle to Senior grades).
You have access to comprehensive student data and must provide highly personalized educational guidance.

CORE OBJECTIVES:
1. Enhance learning through personalized strategies
2. Enable fair academic competition and motivation
3. Support community interaction and peer learning
4. Provide AI-personalized study planning
5. Create effective learning roadmaps based on user data

USER CONTEXT:
{user_context}

CONVERSATION GUIDELINES:
- Always reference the user's specific data when providing advice
- Tailor recommendations to their grade level, learning style, and performance
- Consider their target universities and career goals
- Address their specific strengths and weaknesses
- Provide actionable, time-specific study plans
- Encourage improvement in weak subjects while leveraging strengths
- Use Arabic educational terminology when appropriate
- Be motivational and supportive while maintaining academic rigor

RESPONSE FORMAT:
- Provide specific, actionable advice
- Include time estimates and study schedules when relevant
- Reference their actual performance data
- Suggest specific resources or techniques
- End with encouragement and next steps

Remember: You're not just an AI assistant, you're their personal academic mentor who knows their journey intimately.
"""

    # Include conversation context if available
    if conversation_context:
        system_prompt += f"\n\nPREVIOUS CONVERSATION CONTEXT:\n{conversation_context}"

    try:
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_input}")
        ])
        
        # Initialize the model and chain
        llm = get_chat_model()
        chain = prompt | llm | StrOutputParser()

        # Generate response
        response = chain.invoke({
            "user_input": user_input
        })

        # Return comprehensive response with metadata
        return {
            "response": response,
            "user_profile": {
                "name": user_profile.name,
                "grade_level": user_profile.grade_level,
                "learning_style": user_profile.learning_style
            },
            "success": True,
            "timestamp": parserdb.datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "response": f"I encountered an error while processing your request: {str(e)}",
            "error": str(e),
            "success": False
        }

def get_study_roadmap(user_id: str, subject: str = None, timeframe: str = "month") -> Dict[str, Any]:
    """
    Generate a personalized study roadmap for the user
    
    Args:
        user_id: User identifier
        subject: Specific subject to focus on (optional)
        timeframe: "week", "month", or "semester"
    
    Returns:
        Detailed study roadmap with schedules and milestones
    """
    try:
        user_data = parserdb.user_parser.get_user_data(user_id)
        profile = user_data["profile"]
        courses = user_data["courses"]
        analytics = user_data["analytics"]
        
        # Create focused roadmap prompt
        roadmap_prompt = f"""
Create a detailed {timeframe} study roadmap for this Egyptian student:

STUDENT PROFILE:
- Grade: {profile.grade_level}
- Learning Style: {profile.learning_style}
- Daily Study Hours: {profile.study_hours_per_day}
- Target Universities: {', '.join(profile.target_universities)}

CURRENT PERFORMANCE:
"""
        
        for course in courses:
            roadmap_prompt += f"\n- {course.course_name}: {course.average_grade}% avg, {course.current_progress}% complete"
        
        roadmap_prompt += f"""

LEARNING ANALYTICS:
- Study Streak: {analytics.study_streak} days
- Completion Rate: {analytics.completion_rate}%
- Strengths: {', '.join(analytics.strengths)}
- Weaknesses: {', '.join(analytics.weaknesses)}

{f"FOCUS SUBJECT: {subject}" if subject else "COMPREHENSIVE ROADMAP NEEDED"}

Create a detailed {timeframe} plan with:
1. Weekly/daily schedules
2. Specific learning objectives
3. Time allocations per subject
4. Milestone checkpoints
5. Improvement strategies for weak areas
6. Practice schedules and mock tests
7. University preparation tasks (if applicable)

Format as a structured, actionable plan with specific dates and measurable goals.
"""

        llm = get_chat_model()
        response = llm.invoke([HumanMessage(content=roadmap_prompt)])
        
        return {
            "roadmap": response.content,
            "timeframe": timeframe,
            "focus_subject": subject,
            "success": True
        }
        
    except Exception as e:
        return {
            "roadmap": f"Error generating roadmap: {str(e)}",
            "error": str(e),
            "success": False
        }

def analyze_performance_trends(user_id: str) -> Dict[str, Any]:
    """
    Analyze user's performance trends and provide insights
    """
    try:
        courses = parserdb.get_course_progress(user_id)
        analytics = parserdb.get_learning_analytics(user_id)
        
        analysis_prompt = f"""
Analyze this student's academic performance trends:

COURSE PERFORMANCE DATA:
"""
        
        for course in courses:
            analysis_prompt += f"""
{course.course_name}:
- Average Grade: {course.average_grade}%
- Recent Quiz Scores: {course.quiz_scores}
- Progress: {course.current_progress}%
- Time Spent: {course.time_spent_hours} hours
- Attendance: {course.attendance_rate}%
"""
        
        analysis_prompt += f"""

LEARNING METRICS:
- Improvement Rate: {analytics.improvement_rate}%
- Completion Rate: {analytics.completion_rate}%
- Study Streak: {analytics.study_streak} days

Provide:
1. Performance trend analysis
2. Strengths and improvement areas
3. Specific recommendations
4. Warning signs or concerns
5. Celebration-worthy achievements
"""

        llm = get_chat_model()
        response = llm.invoke([HumanMessage(content=analysis_prompt)])
        
        return {
            "analysis": response.content,
            "overall_trend": "improving" if analytics.improvement_rate > 0 else "declining",
            "success": True
        }
        
    except Exception as e:
        return {
            "analysis": f"Error analyzing performance: {str(e)}",
            "error": str(e),
            "success": False
        }
