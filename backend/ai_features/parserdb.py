"""
Database parser module for extracting and formatting user data for AI consumption.
This module handles user profile data, course progress, grades, and learning analytics.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class UserProfile:
    """User profile data structure"""
    user_id: str
    name: str
    grade_level: str
    school_type: str
    learning_style: str
    preferred_subjects: List[str]
    weak_subjects: List[str]
    study_hours_per_day: float
    target_universities: List[str]

@dataclass
class CourseProgress:
    """Course progress and performance data"""
    course_id: str
    course_name: str
    subject: str
    current_progress: float  # 0-100%
    average_grade: float
    quiz_scores: List[float]
    assignment_scores: List[float]
    attendance_rate: float
    time_spent_hours: float
    difficulty_level: str
    last_activity: datetime

@dataclass
class LearningAnalytics:
    """Learning behavior and performance analytics"""
    study_streak: int  # days
    most_active_time: str  # e.g., "Morning", "Afternoon", "Evening"
    average_session_duration: float  # minutes
    completion_rate: float  # 0-100%
    improvement_rate: float  # grade improvement over time
    strengths: List[str]
    weaknesses: List[str]
    recommended_study_time: float  # hours per day

class UserDataParser:
    """Parses and formats user data for AI consumption"""
    
    def __init__(self):
        self.user_cache = {}
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive user data for AI processing
        In production, this would connect to your actual database
        """
        # Mock data for demonstration - replace with actual database queries
        if user_id in self.user_cache:
            return self.user_cache[user_id]
        
        # Simulate database query
        user_data = self._fetch_user_data_from_db(user_id)
        self.user_cache[user_id] = user_data
        return user_data
    
    def _fetch_user_data_from_db(self, user_id: str) -> Dict[str, Any]:
        """
        Mock database fetch - replace with actual database connection
        """
        # This is mock data - implement your actual database queries here
        mock_profile = UserProfile(
            user_id=user_id,
            name="Ahmed Mohamed",
            grade_level="Grade 11",
            school_type="Public",
            learning_style="Visual",
            preferred_subjects=["Mathematics", "Physics"],
            weak_subjects=["Arabic Literature", "History"],
            study_hours_per_day=3.5,
            target_universities=["Cairo University", "AUC"]
        )
        
        mock_courses = [
            CourseProgress(
                course_id="math_11_01",
                course_name="Advanced Mathematics",
                subject="Mathematics",
                current_progress=78.5,
                average_grade=85.2,
                quiz_scores=[80, 85, 90, 82, 88],
                assignment_scores=[85, 90, 75, 88],
                attendance_rate=92.0,
                time_spent_hours=45.5,
                difficulty_level="Intermediate",
                last_activity=datetime.now() - timedelta(days=1)
            ),
            CourseProgress(
                course_id="physics_11_01",
                course_name="Physics Fundamentals",
                subject="Physics",
                current_progress=65.0,
                average_grade=72.5,
                quiz_scores=[70, 75, 68, 78, 70],
                assignment_scores=[75, 70, 80, 68],
                attendance_rate=88.0,
                time_spent_hours=32.0,
                difficulty_level="Intermediate",
                last_activity=datetime.now() - timedelta(days=2)
            )
        ]
        
        mock_analytics = LearningAnalytics(
            study_streak=12,
            most_active_time="Evening",
            average_session_duration=45.0,
            completion_rate=82.5,
            improvement_rate=15.2,
            strengths=["Problem Solving", "Mathematical Reasoning", "Analytical Thinking"],
            weaknesses=["Time Management", "Essay Writing", "Memorization"],
            recommended_study_time=4.0
        )
        
        return {
            "profile": mock_profile,
            "courses": mock_courses,
            "analytics": mock_analytics,
            "last_updated": datetime.now()
        }
    
    def format_for_ai(self, user_data: Dict[str, Any]) -> str:
        """
        Format user data into a comprehensive string for AI consumption
        """
        profile = user_data["profile"]
        courses = user_data["courses"]
        analytics = user_data["analytics"]
        
        formatted_data = f"""
USER PROFILE:
- Name: {profile.name}
- Grade Level: {profile.grade_level}
- School Type: {profile.school_type}
- Learning Style: {profile.learning_style}
- Study Hours per Day: {profile.study_hours_per_day}
- Target Universities: {', '.join(profile.target_universities)}
- Preferred Subjects: {', '.join(profile.preferred_subjects)}
- Weak Subjects: {', '.join(profile.weak_subjects)}

COURSE PERFORMANCE:
"""
        
        for course in courses:
            formatted_data += f"""
- {course.course_name} ({course.subject}):
  * Progress: {course.current_progress}%
  * Average Grade: {course.average_grade}%
  * Recent Quiz Scores: {course.quiz_scores[-3:]}
  * Attendance Rate: {course.attendance_rate}%
  * Time Spent: {course.time_spent_hours} hours
  * Difficulty Level: {course.difficulty_level}
"""
        
        formatted_data += f"""
LEARNING ANALYTICS:
- Current Study Streak: {analytics.study_streak} days
- Most Active Study Time: {analytics.most_active_time}
- Average Session Duration: {analytics.average_session_duration} minutes
- Overall Completion Rate: {analytics.completion_rate}%
- Improvement Rate: {analytics.improvement_rate}%
- Strengths: {', '.join(analytics.strengths)}
- Weaknesses: {', '.join(analytics.weaknesses)}
- Recommended Daily Study Time: {analytics.recommended_study_time} hours

RECOMMENDATIONS NEEDED:
Based on this data, the student needs personalized guidance for:
1. Improving performance in weak subjects
2. Optimizing study schedule and time management
3. Preparing for target universities
4. Addressing identified weaknesses while leveraging strengths
"""
        
        return formatted_data
    
    def get_course_specific_data(self, user_id: str, subject: str) -> Optional[CourseProgress]:
        """Get data for a specific course/subject"""
        user_data = self.get_user_data(user_id)
        courses = user_data.get("courses", [])
        
        for course in courses:
            if course.subject.lower() == subject.lower():
                return course
        return None
    
    def update_user_progress(self, user_id: str, course_id: str, new_score: float):
        """Update user progress (for real-time learning tracking)"""
        # In production, this would update the database
        if user_id in self.user_cache:
            courses = self.user_cache[user_id].get("courses", [])
            for course in courses:
                if course.course_id == course_id:
                    course.quiz_scores.append(new_score)
                    # Recalculate average
                    course.average_grade = sum(course.quiz_scores) / len(course.quiz_scores)
                    break

# Global instance for easy importing
user_parser = UserDataParser()

def get_user_context(user_id: str) -> str:
    """
    Main function to get formatted user context for AI
    """
    user_data = user_parser.get_user_data(user_id)
    return user_parser.format_for_ai(user_data)

def get_user_profile(user_id: str) -> UserProfile:
    """Get user profile data"""
    user_data = user_parser.get_user_data(user_id)
    return user_data["profile"]

def get_course_progress(user_id: str) -> List[CourseProgress]:
    """Get all course progress data"""
    user_data = user_parser.get_user_data(user_id)
    return user_data["courses"]

def get_learning_analytics(user_id: str) -> LearningAnalytics:
    """Get learning analytics data"""
    user_data = user_parser.get_user_data(user_id)
    return user_data["analytics"]