import sqlite3
import json
import random
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path - adjust based on your Django project structure
BASE_DIR = Path(__file__).resolve().parent.parent / "src" / "backend"
DB_PATH = BASE_DIR / "db.sqlite3"

@dataclass
class UserProfile:
    """Complete user profile data structure"""
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    score: int
    grade: str
    
    # Additional fields that could be added to Student model
    school_id: Optional[int] = None
    school_name: Optional[str] = None
    bio: Optional[str] = None
    learning_style: str = "mixed"
    study_hours_per_day: int = 2
    profile_visibility: str = "public"
    
    def to_dict(self):
        data = asdict(self)
        if self.date_joined:
            data['date_joined'] = self.date_joined.isoformat()
        return data

@dataclass
class CourseProgress:
    """Course progress tracking"""
    user_id: int
    subject: str
    grade_level: str
    current_score: float
    total_questions_attempted: int
    correct_answers: int
    incorrect_answers: int
    accuracy_percentage: float
    time_spent_minutes: int
    last_activity: datetime
    improvement_rate: float  # percentage improvement over time
    difficulty_level: str
    
    def to_dict(self):
        data = asdict(self)
        if self.last_activity:
            data['last_activity'] = self.last_activity.isoformat()
        return data

@dataclass
class SchoolData:
    """School information"""
    id: int
    name: str
    code: str
    city: str
    governorate: str
    is_active: bool
    
    def to_dict(self):
        return asdict(self)

@dataclass
class StudyGroupData:
    """Study group information"""
    id: int
    name: str
    description: str
    subject: str
    grade_level: str
    max_members: int
    current_member_count: int
    is_private: bool
    created_by_username: str
    created_at: datetime
    
    def to_dict(self):
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class KnockoutRecord:
    """1v1 Knockout game record"""
    id: int
    student1_id: int
    student2_id: int
    winner_id: Optional[int]
    subject: str
    difficulty: str
    score_student1: int
    score_student2: int
    created_at: datetime
    completed_at: Optional[datetime]
    
    def to_dict(self):
        data = asdict(self)
        # Convert datetime objects to strings for JSON serialization
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data

@dataclass
class PostData:
    """Post/Reel data structure"""
    id: int
    author_id: int
    author_username: str
    caption: str
    description: str
    likes: int
    created_at: datetime
    
    def to_dict(self):
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class CommentData:
    """Comment data structure"""
    id: int
    author_id: int
    author_username: str
    body: str
    likes: int
    post_id: Optional[int]
    created_at: datetime
    
    def to_dict(self):
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class LearningAnalytics:
    """Learning analytics and performance metrics with enhanced calculations"""
    user_id: int
    total_knockouts: int
    wins: int
    losses: int
    win_rate: float
    total_points: int
    favorite_subjects: List[str]
    weak_subjects: List[str]
    study_streak: int
    avg_score: float
    improvement_trend: str
    
    # Enhanced analytics
    weekly_activity_score: float
    subject_mastery_levels: Dict[str, float]  # subject -> mastery percentage
    learning_velocity: float  # points gained per day
    consistency_score: float  # how consistent their study habits are
    challenge_preference: str  # "easy", "medium", "hard"
    peak_performance_time: str  # best time of day for performance
    social_engagement_score: float  # interaction with posts/comments
    
    # Course-specific analytics
    course_progress_summary: Dict[str, Dict[str, Any]]  # subject -> progress data
    
    def to_dict(self):
        return asdict(self)

class DatabaseFetcher:
    """Enhanced database fetcher for the educational platform"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Comprehensive database validation and setup"""
        try:
            # Check if database file exists
            if not os.path.exists(self.db_path):
                logger.error(f"Database file not found: {self.db_path}")
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
            # Check if file is readable
            if not os.access(self.db_path, os.R_OK):
                logger.error(f"Database file is not readable: {self.db_path}")
                raise PermissionError(f"Database file is not readable: {self.db_path}")
            
            # Test connection and validate tables
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                required_tables = ['core_user', 'dof3a_base_student', 'dof3a_base_comment', 'dof3a_base_post']
                existing_tables = [table[0] for table in tables]
                
                missing_tables = [table for table in required_tables if table not in existing_tables]
                if missing_tables:
                    logger.warning(f"Missing required tables: {missing_tables}")
                    # Don't raise error, just log warning as tables might be created later
                
                logger.info("✅ Database validation successful")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Database validation error: {e}")
            raise sqlite3.Error(f"Database validation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during database validation: {e}")
            raise Exception(f"Database validation failed: {e}")
    
    def _get_connection(self):
        """Get database connection with comprehensive error handling"""
        try:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
                
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            
            # Test the connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise sqlite3.Error(f"Failed to connect to database: {e}")
        except Exception as e:
            logger.error(f"Unexpected database connection error: {e}")
            raise Exception(f"Database connection failed: {e}")
    
    def _validate_user_id(self, user_id: Any) -> int:
        """Validate and sanitize user ID input"""
        if user_id is None:
            raise ValueError("User ID cannot be None")
        
        try:
            user_id = int(user_id)
            if user_id <= 0:
                raise ValueError("User ID must be a positive integer")
            return user_id
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid user ID: {user_id}. Must be a positive integer.")
    
    def _validate_limit(self, limit: Any) -> int:
        """Validate and sanitize limit parameter"""
        if limit is None:
            return 10  # Default limit
        
        try:
            limit = int(limit)
            if limit <= 0:
                raise ValueError("Limit must be a positive integer")
            if limit > 1000:  # Prevent excessive queries
                logger.warning(f"Limit {limit} exceeds maximum, using 1000")
                return 1000
            return limit
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid limit: {limit}. Must be a positive integer.")
    
    def _sanitize_string(self, value: Any) -> str:
        """Sanitize string input to prevent SQL injection"""
        if value is None:
            return ""
        
        try:
            # Convert to string and strip whitespace
            sanitized = str(value).strip()
            
            # Remove potentially harmful characters
            dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '')
            
            return sanitized
        except Exception as e:
            logger.warning(f"String sanitization failed: {e}")
            return ""
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """
        Fetch complete user profile including student data with comprehensive validation
        
        Args:
            user_id: User ID
            
        Returns:
            UserProfile object or None if not found
            
        Raises:
            ValueError: If user_id is invalid
            sqlite3.Error: If database query fails
        """
        try:
            # Validate input
            user_id = self._validate_user_id(user_id)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Join User and Student tables - Updated to match actual Django structure
                query = """
                SELECT 
                    u.id as user_id,
                    u.username,
                    u.email,
                    u.first_name,
                    u.last_name,
                    u.is_active,
                    COALESCE(s.score, 0) as score,
                    COALESCE(s.grade, 'Please select an option') as grade
                FROM core_user u
                LEFT JOIN dof3a_base_student s ON u.id = s.user_id
                WHERE u.id = ? AND u.is_active = 1
                """
                
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    logger.info(f"User with ID {user_id} not found or inactive")
                    return None
                
                # Safely parse date
                try:
                    join_date = datetime.fromisoformat(row['date_joined'].replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Invalid date format for user {user_id}: {e}")
                    join_date = datetime.now()
                
                # Create and validate UserProfile
                profile = UserProfile(
                    user_id=row['user_id'],
                    username=self._sanitize_string(row['username']) or f"user_{user_id}",
                    email=self._sanitize_string(row['email']) or "",
                    first_name=self._sanitize_string(row['first_name']) or "",
                    last_name=self._sanitize_string(row['last_name']) or "",
                    grade=self._sanitize_string(row['grade']) or "Please select an option",
                    score=max(0, int(row['score']) if row['score'] is not None else 0),
                    join_date=join_date,
                    is_active=bool(row['is_active'])
                )
                
                logger.info(f"Successfully retrieved user profile for ID {user_id}")
                return profile
                
        except ValueError as e:
            logger.error(f"Validation error in get_user_profile: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Database error in get_user_profile: {e}")
            raise sqlite3.Error(f"Failed to fetch user profile: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in get_user_profile: {e}")
            raise Exception(f"Failed to fetch user profile: {e}")

    def get_user_posts(self, user_id: int, limit: int = 10) -> List[PostData]:
        """
        Fetch user's posts/reels with comprehensive validation
        
        Args:
            user_id: User ID
            limit: Maximum number of posts to return
            
        Returns:
            List of PostData objects
            
        Raises:
            ValueError: If inputs are invalid
            sqlite3.Error: If database query fails
        """
        try:
            # Validate inputs
            user_id = self._validate_user_id(user_id)
            limit = self._validate_limit(limit)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT
                    p.id,
                    p.author_id,
                    u.username as author_username,
                    p.caption,
                    p.description,
                    p.likes,
                    p.created_at
                FROM dof3a_base_post p
                JOIN core_user u ON p.author_id = u.id
                WHERE p.author_id = ?
                ORDER BY p.created_at DESC
                LIMIT ?
                """
                
                cursor.execute(query, (user_id, limit))
                rows = cursor.fetchall()
                
                posts = []
                for row in rows:
                    try:
                        # Safely parse created_at
                        created_at = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        created_at = datetime.now()
                    
                    post = PostData(
                        id=row['id'],
                        author_id=row['author_id'],
                        author_username=self._sanitize_string(row['author_username']),
                        caption=self._sanitize_string(row['caption']),
                        description=self._sanitize_string(row['description']),
                        likes=max(0, int(row['likes']) if row['likes'] is not None else 0),
                        created_at=created_at
                    )
                    posts.append(post)
                
                logger.info(f"Successfully retrieved {len(posts)} posts for user {user_id}")
                return posts
                
        except ValueError as e:
            logger.error(f"Validation error in get_user_posts: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Database error in get_user_posts: {e}")
            raise sqlite3.Error(f"Failed to fetch user posts: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in get_user_posts: {e}")
    def get_comprehensive_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get all user data in one comprehensive dictionary with validation
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing all user data
            
        Raises:
            ValueError: If user_id is invalid
            Exception: If data retrieval fails
        """
        try:
            user_id = self._validate_user_id(user_id)
            
            logger.info(f"Fetching comprehensive data for user {user_id}")
            
            # Initialize data containers with defaults
            data = {
                "user_id": user_id,
                "profile": None,
                "posts": [],
                "comments": [],
                "course_progress": [],
                "learning_analytics": None,
                "social_activity": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Fetch each data type with individual error handling
            try:
                data["profile"] = self.get_user_profile(user_id)
                if data["profile"]:
                    data["profile"] = data["profile"].to_dict()
            except Exception as e:
                logger.warning(f"Failed to fetch profile for user {user_id}: {e}")
            
            try:
                posts = self.get_user_posts(user_id, 20)
                data["posts"] = [post.to_dict() for post in posts]
            except Exception as e:
                logger.warning(f"Failed to fetch posts for user {user_id}: {e}")
            
            try:
                data["course_progress"] = self.get_course_progress(user_id)
                data["course_progress"] = [cp.to_dict() for cp in data["course_progress"]]
            except Exception as e:
                logger.warning(f"Failed to fetch course progress for user {user_id}: {e}")
            
            try:
                analytics = self.get_learning_analytics(user_id)
                if analytics:
                    data["learning_analytics"] = analytics.to_dict()
            except Exception as e:
                logger.warning(f"Failed to fetch analytics for user {user_id}: {e}")
            
            logger.info(f"Successfully compiled comprehensive data for user {user_id}")
            return data
            
        except ValueError as e:
            logger.error(f"Validation error in get_comprehensive_user_data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_comprehensive_user_data: {e}")
            raise Exception(f"Failed to fetch comprehensive user data: {e}")
    
    def get_formatted_user_context(self, user_id: int) -> str:
        """
        Get formatted user context string for AI with validation
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted string with user context
            
        Raises:
            ValueError: If user_id is invalid
        """
        try:
            user_id = self._validate_user_id(user_id)
            
            comprehensive_data = self.get_comprehensive_user_data(user_id)
            profile = comprehensive_data.get("profile")
            analytics = comprehensive_data.get("learning_analytics")
            
            if not profile:
                return f"User ID {user_id}: Profile not found or inaccessible."
            
            context = f"""
USER PROFILE:
- User ID: {profile['user_id']}
- Username: {profile['username']}
- Grade: {profile['grade']}
- Score: {profile['score']} points
- Join Date: {profile['join_date'][:10] if profile.get('join_date') else 'Unknown'}
- Activity Status: {'Active' if profile.get('is_active') else 'Inactive'}

LEARNING ANALYTICS:
"""
            
            if analytics:
                context += f"""- Total Knockout Games: {analytics.get('total_knockouts', 0)}
- Win Rate: {analytics.get('win_rate', 0):.1f}%
- Total Points: {analytics.get('total_points', 0)}
- Current Streak: {analytics.get('current_streak', 0)} days
- Average Session: {analytics.get('avg_session_length', 0):.1f} minutes
- Study Hours: {analytics.get('total_study_hours', 0):.1f} hours
"""
            else:
                context += "- No analytics data available\n"
            
            context += f"""
ACTIVITY SUMMARY:
- Posts Created: {len(comprehensive_data.get('posts', []))}
- Course Progress: {len(comprehensive_data.get('course_progress', []))} subjects tracked
- Last Activity: {comprehensive_data.get('timestamp', 'Unknown')}
"""
            
            return context.strip()
            
        except ValueError as e:
            logger.error(f"Validation error in get_formatted_user_context: {e}")
            return f"Error: {e}"
        except Exception as e:
            logger.error(f"Error formatting user context for {user_id}: {e}")
            return f"User ID {user_id}: Context temporarily unavailable due to system error."
    
    def get_course_progress(self, user_id: int) -> List[CourseProgress]:
        """
        Get user's course progress with validation
        
        Args:
            user_id: User ID
            
        Returns:
            List of CourseProgress objects
            
        Raises:
            ValueError: If user_id is invalid
            sqlite3.Error: If database query fails
        """
        try:
            user_id = self._validate_user_id(user_id)
            
            # Since we don't have a course progress table yet, simulate realistic data
            subjects = ["Mathematics", "Science", "Arabic", "English", "Social Studies"]
            progress_list = []
            
            for i, subject in enumerate(subjects):
                # Generate realistic progress data
                completion = random.randint(10, 95)
                grade = random.choice(["A", "B", "C", "D"])
                
                progress = CourseProgress(
                    user_id=user_id,
                    subject=subject,
                    current_unit=f"Unit {random.randint(1, 12)}",
                    completion_percentage=completion,
                    last_accessed=datetime.now() - timedelta(days=random.randint(0, 30)),
                    grade=grade,
                    points_earned=random.randint(50, 500),
                    assignments_completed=random.randint(1, 20),
                    total_assignments=random.randint(15, 25)
                )
                progress_list.append(progress)
            
            logger.info(f"Generated course progress data for user {user_id}")
            return progress_list
            
        except ValueError as e:
            logger.error(f"Validation error in get_course_progress: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating course progress for user {user_id}: {e}")
            return []
    
    def get_learning_analytics(self, user_id: int) -> Optional[LearningAnalytics]:
        """
        Calculate comprehensive learning analytics with validation
        
        Args:
            user_id: User ID
            
        Returns:
            LearningAnalytics object or None
            
        Raises:
            ValueError: If user_id is invalid
        """
        try:
            user_id = self._validate_user_id(user_id)
            
            # Since we don't have knockout/analytics tables yet, generate realistic data
            total_knockouts = random.randint(5, 100)
            wins = random.randint(0, total_knockouts)
            losses = total_knockouts - wins
            win_rate = (wins / total_knockouts * 100) if total_knockouts > 0 else 0
            
            analytics = LearningAnalytics(
                user_id=user_id,
                total_knockouts=total_knockouts,
                wins=wins,
                losses=losses,
                win_rate=win_rate,
                total_points=random.randint(100, 5000),
                current_streak=random.randint(0, 30),
                longest_streak=random.randint(0, 45),
                avg_session_length=random.uniform(15.0, 60.0),
                total_study_hours=random.uniform(10.0, 200.0),
                subjects_studied=random.randint(3, 8),
                favorite_subject=random.choice(["Math", "Science", "Arabic", "English"]),
                weakest_subject=random.choice(["Math", "Science", "Arabic", "English"]),
                total_sessions=random.randint(10, 200),
                last_activity=datetime.now() - timedelta(days=random.randint(0, 7))
            )
            
            logger.info(f"Generated learning analytics for user {user_id}")
            return analytics
            
        except ValueError as e:
            logger.error(f"Validation error in get_learning_analytics: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating learning analytics for user {user_id}: {e}")
            return None
        """
        Fetch user's posts/reels
        
        Args:
            user_id: User ID
            limit: Maximum number of posts to return
            
        Returns:
            List of PostData objects
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    p.id,
                    p.author_id,
                    u.username as author_username,
                    p.caption,
                    p.description,
                    p.likes,
                    datetime('now') as created_at
                FROM dof3a_base_post p
                JOIN core_user u ON p.author_id = u.id
                WHERE p.author_id = ?
                ORDER BY p.id DESC
                LIMIT ?
                """
                
                cursor.execute(query, (user_id, limit))
                rows = cursor.fetchall()
                
                posts = []
                for row in rows:
                    posts.append(PostData(
                        id=row['id'],
                        author_id=row['author_id'],
                        author_username=row['author_username'],
                        caption=row['caption'],
                        description=row['description'],
                        likes=row['likes'],
                        created_at=datetime.now()  # Since created_at doesn't exist in current model
                    ))
                
                return posts
                
        except sqlite3.Error as e:
            print(f"Error fetching user posts: {e}")
            return []
    
    def get_user_comments(self, user_id: int, limit: int = 10) -> List[CommentData]:
        """
        Fetch user's comments
        
        Args:
            user_id: User ID
            limit: Maximum number of comments to return
            
        Returns:
            List of CommentData objects
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    c.id,
                    c.author_id,
                    u.username as author_username,
                    c.body,
                    c.likes,
                    datetime('now') as created_at
                FROM dof3a_base_comment c
                JOIN core_user u ON c.author_id = u.id
                WHERE c.author_id = ?
                ORDER BY c.id DESC
                LIMIT ?
                """
                
                cursor.execute(query, (user_id, limit))
                rows = cursor.fetchall()
                
                comments = []
                for row in rows:
                    comments.append(CommentData(
                        id=row['id'],
                        author_id=row['author_id'],
                        author_username=row['author_username'],
                        body=row['body'],
                        likes=row['likes'],
                        post_id=None,  # Not linked in current model
                        created_at=datetime.now()
                    ))
                
                return comments
                
        except sqlite3.Error as e:
            print(f"Error fetching user comments: {e}")
            return []
    
    def get_learning_analytics(self, user_id: int) -> LearningAnalytics:
        """
        Calculate and return enhanced learning analytics for the user
        
        Args:
            user_id: User ID
            
        Returns:
            LearningAnalytics object with comprehensive metrics
        """
        try:
            # Get user profile and course progress
            profile = self.get_user_profile(user_id)
            course_progress = self.get_course_progress(user_id)
            posts = self.get_user_posts(user_id, 10)
            comments = self.get_user_comments(user_id, 10)
            
            current_score = profile.score if profile else 0
            
            # Calculate enhanced analytics
            total_questions = sum(cp.total_questions_attempted for cp in course_progress)
            total_correct = sum(cp.correct_answers for cp in course_progress)
            overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            # Calculate subject mastery levels
            subject_mastery = {}
            for cp in course_progress:
                subject_mastery[cp.subject] = cp.accuracy_percentage
            
            # Calculate learning velocity (points per day since joining)
            days_since_joined = (datetime.now() - profile.date_joined).days if profile else 1
            learning_velocity = current_score / max(days_since_joined, 1)
            
            # Calculate weekly activity score
            recent_activity = len(posts) + len(comments)
            weekly_activity_score = min(100, recent_activity * 10)  # Cap at 100
            
            # Determine favorite and weak subjects based on course progress
            if course_progress:
                sorted_by_accuracy = sorted(course_progress, key=lambda x: x.accuracy_percentage, reverse=True)
                favorite_subjects = [cp.subject for cp in sorted_by_accuracy[:3]]
                weak_subjects = [cp.subject for cp in sorted_by_accuracy[-2:] if cp.accuracy_percentage < 70]
            else:
                favorite_subjects = self._get_favorite_subjects(user_id)
                weak_subjects = self._get_weak_subjects(user_id)
            
            # Calculate improvement trend
            improvement_scores = [cp.improvement_rate for cp in course_progress if cp.improvement_rate != 0]
            avg_improvement = sum(improvement_scores) / len(improvement_scores) if improvement_scores else 0
            
            if avg_improvement > 5:
                improvement_trend = "improving"
            elif avg_improvement < -5:
                improvement_trend = "declining"
            else:
                improvement_trend = "stable"
            
            # Calculate consistency score based on recent activity
            consistency_score = min(100, self._calculate_study_streak(user_id) * 10)
            
            # Determine challenge preference based on accuracy
            if overall_accuracy > 85:
                challenge_preference = "hard"
            elif overall_accuracy > 70:
                challenge_preference = "medium"
            else:
                challenge_preference = "easy"
            
            # Course progress summary
            course_summary = {}
            for cp in course_progress:
                course_summary[cp.subject] = {
                    "accuracy": cp.accuracy_percentage,
                    "questions_attempted": cp.total_questions_attempted,
                    "time_spent": cp.time_spent_minutes,
                    "improvement_rate": cp.improvement_rate,
                    "last_activity": cp.last_activity.isoformat()
                }
            
            analytics = LearningAnalytics(
                user_id=user_id,
                total_knockouts=random.randint(0, 20),  # Mock data
                wins=random.randint(0, 15),
                losses=random.randint(0, 10),
                win_rate=overall_accuracy * 0.8,  # Approximate win rate from accuracy
                total_points=current_score,
                favorite_subjects=favorite_subjects,
                weak_subjects=weak_subjects,
                study_streak=self._calculate_study_streak(user_id),
                avg_score=overall_accuracy,
                improvement_trend=improvement_trend,
                weekly_activity_score=weekly_activity_score,
                subject_mastery_levels=subject_mastery,
                learning_velocity=learning_velocity,
                consistency_score=consistency_score,
                challenge_preference=challenge_preference,
                social_engagement_score=min(100, recent_activity * 5),
                course_progress_summary=course_summary
            )
            
            return analytics
            
        except Exception as e:
            print(f"Error calculating learning analytics: {e}")
            return self._create_default_analytics(user_id)
    
    def get_course_progress(self, user_id: int) -> List[CourseProgress]:
        """
        Get course progress for all subjects
        
        Args:
            user_id: User ID
            
        Returns:
            List of CourseProgress objects
        """
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                return []
            
            # Since we don't have actual course progress tables yet,
            # we'll simulate based on user's grade and activity
            subjects = self._get_grade_subjects(profile.grade)
            course_progress = []
            
            for subject in subjects:
                # Simulate course progress based on current score and random variations
                base_score = min(profile.score / 10, 100)  # Normalize score
                accuracy = max(50, min(95, base_score + random.randint(-15, 15)))
                questions_attempted = random.randint(20, 200)
                correct_answers = int(questions_attempted * accuracy / 100)
                
                progress = CourseProgress(
                    user_id=user_id,
                    subject=subject,
                    grade_level=profile.grade,
                    current_score=accuracy,
                    total_questions_attempted=questions_attempted,
                    correct_answers=correct_answers,
                    incorrect_answers=questions_attempted - correct_answers,
                    accuracy_percentage=accuracy,
                    time_spent_minutes=random.randint(60, 500),
                    last_activity=datetime.now() - timedelta(days=random.randint(0, 7)),
                    improvement_rate=random.uniform(-5, 15),
                    difficulty_level="medium"
                )
                course_progress.append(progress)
            
            return course_progress
            
        except Exception as e:
            print(f"Error getting course progress: {e}")
            return []
    
    def get_study_groups_for_user(self, user_id: int) -> List[StudyGroupData]:
        """
        Get study groups that the user is part of
        Note: This is mock data until study group tables are implemented
        
        Args:
            user_id: User ID
            
        Returns:
            List of StudyGroupData objects
        """
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                return []
            
            # Mock study groups based on user's grade and subjects
            subjects = self._get_grade_subjects(profile.grade)
            study_groups = []
            
            # Create 2-3 mock study groups
            for i, subject in enumerate(subjects[:3]):
                group = StudyGroupData(
                    id=i + 1,
                    name=f"{subject} Study Group - {profile.grade}",
                    description=f"Collaborative study group for {subject} students in {profile.grade}",
                    subject=subject,
                    grade_level=profile.grade,
                    max_members=8,
                    current_member_count=random.randint(3, 7),
                    is_private=False,
                    created_by_username="study_leader",
                    created_at=datetime.now() - timedelta(days=random.randint(10, 60))
                )
                study_groups.append(group)
            
            return study_groups
            
        except Exception as e:
            print(f"Error getting study groups: {e}")
            return []
    
    def get_knockout_history(self, user_id: int, limit: int = 10) -> List[KnockoutRecord]:
        """
        Get knockout game history for user
        Note: This is mock data until knockout tables are implemented
        
        Args:
            user_id: User ID
            limit: Maximum records to return
            
        Returns:
            List of KnockoutRecord objects
        """
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                return []
            
            subjects = self._get_grade_subjects(profile.grade)
            knockouts = []
            
            # Generate mock knockout history
            for i in range(min(limit, 5)):
                subject = random.choice(subjects)
                opponent_id = random.randint(2, 100)  # Mock opponent
                user_score = random.randint(5, 10)
                opponent_score = random.randint(3, 9)
                winner = user_id if user_score > opponent_score else opponent_id
                
                knockout = KnockoutRecord(
                    id=i + 1,
                    student1_id=user_id,
                    student2_id=opponent_id,
                    winner_id=winner,
                    subject=subject,
                    difficulty=random.choice(['easy', 'medium', 'hard']),
                    score_student1=user_score,
                    score_student2=opponent_score,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    completed_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                knockouts.append(knockout)
            
            return knockouts
            
        except Exception as e:
            print(f"Error getting knockout history: {e}")
            return []
    
    def get_school_info(self, school_id: int) -> Optional[SchoolData]:
        """
        Get school information
        Note: This is mock data until school tables are implemented
        """
        # Mock school data
        schools = {
            1: SchoolData(1, "Cairo Modern School", "CMS001", "Cairo", "Cairo", True),
            2: SchoolData(2, "Alexandria International School", "AIS002", "Alexandria", "Alexandria", True),
            3: SchoolData(3, "Giza STEM School", "GSS003", "Giza", "Giza", True),
        }
        return schools.get(school_id)
    
    def _get_grade_subjects(self, grade: str) -> List[str]:
        """Get subjects for a specific grade level"""
        if "Middle" in grade:
            return ["Math", "Science", "Arabic", "English", "Social Studies"]
        elif "Senior" in grade:
            return ["Math", "Physics", "Chemistry", "Biology", "Arabic", "English"]
        else:
            return ["Math", "Science", "Arabic", "English"]
    
    def _calculate_study_streak(self, user_id: int) -> int:
        """Calculate user's current study streak"""
        # Mock implementation - in real app, track daily activity
        return random.randint(1, 10)
    
    def _create_default_analytics(self, user_id: int) -> LearningAnalytics:
        """Create default analytics when calculation fails"""
        return LearningAnalytics(
            user_id=user_id,
            total_knockouts=0,
            wins=0,
            losses=0,
            win_rate=0.0,
            total_points=0,
            favorite_subjects=[],
            weak_subjects=[],
            study_streak=0,
            avg_score=0.0,
            improvement_trend="stable",
            weekly_activity_score=0.0,
            subject_mastery_levels={},
            learning_velocity=0.0,
            consistency_score=0.0,
            challenge_preference="medium",
            peak_performance_time="afternoon",
            social_engagement_score=0.0,
            course_progress_summary={}
        )
    
    def _get_favorite_subjects(self, user_id: int) -> List[str]:
        """Get user's favorite subjects based on activity"""
        # Mock implementation - in real app, analyze knockout performance
        profile = self.get_user_profile(user_id)
        if profile and profile.grade:
            if "Middle" in profile.grade:
                return ["Math", "Science", "Arabic"]
            else:
                return ["Physics", "Chemistry", "Math"]
        return ["Math", "Science"]
    
    def _get_weak_subjects(self, user_id: int) -> List[str]:
        """Get user's weak subjects based on performance"""
        # Mock implementation - in real app, analyze knockout losses
        profile = self.get_user_profile(user_id)
        if profile and profile.grade:
            if "Middle" in profile.grade:
                return ["English", "History"]
            else:
                return ["Biology", "Arabic"]
        return ["English"]
    
    def get_comprehensive_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get all user data for LLM processing including enhanced features
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing all user data
        """
        profile = self.get_user_profile(user_id)
        posts = self.get_user_posts(user_id, 5)
        comments = self.get_user_comments(user_id, 5)
        analytics = self.get_learning_analytics(user_id)
        course_progress = self.get_course_progress(user_id)
        study_groups = self.get_study_groups_for_user(user_id)
        knockout_history = self.get_knockout_history(user_id, 5)
        
        return {
            "profile": profile.to_dict() if profile else None,
            "posts": [post.to_dict() for post in posts],
            "comments": [comment.to_dict() for comment in comments],
            "analytics": analytics.to_dict(),
            "course_progress": [cp.to_dict() for cp in course_progress],
            "study_groups": [sg.to_dict() for sg in study_groups],
            "knockout_history": [ko.to_dict() for ko in knockout_history],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_formatted_user_context(self, user_id: int) -> str:
        """
        Get formatted user context string for LLM
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted string with user context
        """
        data = self.get_comprehensive_user_data(user_id)
        
        if not data["profile"]:
            return f"User {user_id} not found in database."
        
        profile = data["profile"]
        analytics = data["analytics"]
        
        context = f"""
=== USER PROFILE ===
Name: {profile['first_name']} {profile['last_name']} (@{profile['username']})
Email: {profile['email']}
Grade Level: {profile['grade']}
Current Score: {profile['score']} points
Account Created: {profile['date_joined'][:10]}
Account Status: {'Active' if profile['is_active'] else 'Inactive'}

=== LEARNING ANALYTICS ===
Total Points: {analytics['total_points']}
Study Streak: {analytics['study_streak']} days
Average Score: {analytics['avg_score']:.1f}
Performance Trend: {analytics['improvement_trend']}
Favorite Subjects: {', '.join(analytics['favorite_subjects'])}
Areas for Improvement: {', '.join(analytics['weak_subjects'])}

=== RECENT ACTIVITY ===
Recent Posts: {len(data['posts'])} posts
Recent Comments: {len(data['comments'])} comments
Platform Engagement: {'High' if len(data['posts']) + len(data['comments']) > 5 else 'Moderate' if len(data['posts']) + len(data['comments']) > 2 else 'Low'}

=== EDUCATIONAL CONTEXT ===
Grade Level Details: {profile['grade']}
Learning Focus: {self._get_grade_focus(profile['grade'])}
University Preparation: {self._get_university_prep_status(profile['grade'])}
"""
        
        return context.strip()
    
    def _get_grade_focus(self, grade: str) -> str:
        """Get educational focus for grade level"""
        if "Middle" in grade:
            return "Foundation building, core concepts, basic skills development"
        elif "Senior" in grade:
            return "Advanced concepts, university preparation, specialization"
        else:
            return "General education"
    
    def _get_university_prep_status(self, grade: str) -> str:
        """Get university preparation status"""
        if grade == "Senior 3":
            return "Final year - intensive university exam preparation"
        elif grade in ["Senior 1", "Senior 2"]:
            return "Active university preparation phase"
        else:
            return "Pre-university foundation building"
    
    def search_users_by_grade(self, grade: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for users by grade level
        
        Args:
            grade: Grade level to search for
            limit: Maximum number of users to return
            
        Returns:
            List of user dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    u.id,
                    u.username,
                    u.first_name,
                    u.last_name,
                    s.score,
                    s.grade
                FROM core_user u
                JOIN dof3a_base_student s ON u.id = s.user_id
                WHERE s.grade = ? AND u.is_active = 1
                ORDER BY s.score DESC
                LIMIT ?
                """
                
                cursor.execute(query, (grade, limit))
                rows = cursor.fetchall()
                
                users = []
                for row in rows:
                    users.append({
                        'id': row['id'],
                        'username': row['username'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'score': row['score'],
                        'grade': row['grade']
                    })
                
                return users
                
        except sqlite3.Error as e:
            print(f"Error searching users by grade: {e}")
            return []

# Global instance for easy access
db_fetcher = DatabaseFetcher()

# Convenience functions for backward compatibility
def get_user_profile(user_id: int) -> Optional[UserProfile]:
    """Get user profile - convenience function"""
    return db_fetcher.get_user_profile(user_id)

def get_user_context(user_id: int) -> str:
    """Get formatted user context - convenience function"""
    return db_fetcher.get_formatted_user_context(user_id)

def get_learning_analytics(user_id: int) -> LearningAnalytics:
    """Get learning analytics - convenience function"""
    return db_fetcher.get_learning_analytics(user_id)

def get_comprehensive_data(user_id: int) -> Dict[str, Any]:
    """Get all user data - convenience function"""
    return db_fetcher.get_comprehensive_user_data(user_id)

def get_course_progress(user_id: int) -> List[CourseProgress]:
    """Get course progress - convenience function"""
    return db_fetcher.get_course_progress(user_id)

def get_study_groups(user_id: int) -> List[StudyGroupData]:
    """Get study groups - convenience function"""
    return db_fetcher.get_study_groups_for_user(user_id)

def get_knockout_history(user_id: int, limit: int = 10) -> List[KnockoutRecord]:
    """Get knockout history - convenience function"""
    return db_fetcher.get_knockout_history(user_id, limit)

def get_school_info(school_id: int) -> Optional[SchoolData]:
    """Get school information - convenience function"""
    return db_fetcher.get_school_info(school_id)

# Test function
def test_database_connection():
    """Test database connection and fetch sample data"""
    try:
        # Test with user ID 1
        profile = get_user_profile(1)
        if profile:
            print("✅ Database connection successful!")
            print(f"Sample user: {profile.username} ({profile.grade})")
            return True
        else:
            print("⚠️ Database connected but no users found")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test the database connection
    test_database_connection()
    
    # Example usage
    try:
        user_context = get_user_context(1)
        print("\n=== SAMPLE USER CONTEXT ===")
        print(user_context)
    except Exception as e:
        print(f"Error getting user context: {e}")
