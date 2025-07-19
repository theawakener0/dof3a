import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
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
    """User profile data structure matching Django models"""
    username: str
    email: str
    score: int
    grade: str
    
    def to_dict(self):
        data = asdict(self)
        data['date_joined'] = self.date_joined.isoformat()
        return data

@dataclass
class PostData:
    """Post data structure matching Django models"""
    id: int
    author_id: int
    author_username: str
    caption: str
    description: str
    likes: int
    
    def to_dict(self):
        return asdict(self)

@dataclass
class CommentData:
    """Comment data structure matching Django models"""
    id: int
    author_id: int
    author_username: str
    body: str
    likes: int
    
    def to_dict(self):
        return asdict(self)

class DatabaseFetcher:
    """Database fetcher for the educational platform - only actual Django models"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Check if database exists and is accessible"""
        try:
            if not Path(self.db_path).exists():
                logger.error(f"Database file not found: {self.db_path}")
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
            # Test connection
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                required_tables = ['core_user', 'dof3a_base_student', 'dof3a_base_post', 'dof3a_base_comment']
                existing_tables = [table['name'] for table in tables]
                
                for table in required_tables:
                    if table not in existing_tables:
                        logger.warning(f"Required table '{table}' not found in database")
                
                logger.info("✅ Database validation successful")
                
        except sqlite3.Error as e:
            logger.error(f"Database validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database validation: {e}")
            raise
    
    def _get_connection(self):
        """Get database connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
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
            return 10
        
        try:
            limit = int(limit)
            return max(1, min(limit, 100))  # Limit between 1 and 100
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid limit value: {limit}, using default of 10")
            return 10
    
    def _sanitize_string(self, value: Any) -> str:
        """Sanitize string input"""
        if value is None:
            return ""
        
        try:
            return str(value).strip()
        except Exception as e:
            logger.warning(f"Failed to sanitize string: {e}")
            return ""
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """
        Fetch user profile including student data
        
        Args:
            user_id: User ID
            
        Returns:
            UserProfile object or None if not found
        """
        try:
            user_id = self._validate_user_id(user_id)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Join User and Student tables
                query = """
                SELECT 
                    u.username,
                    u.email,
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
                
                # Parse date_joined
                try:
                    date_joined = datetime.fromisoformat(row['date_joined'].replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Invalid date format for user {user_id}: {e}")
                    date_joined = datetime.now()
                
                # Create UserProfile
                profile = UserProfile(
                    user_id=row['user_id'],
                    username=self._sanitize_string(row['username']) or f"user_{user_id}",
                    email=self._sanitize_string(row['email']) or "",
                    first_name=self._sanitize_string(row['first_name']) or "",
                    last_name=self._sanitize_string(row['last_name']) or "",
                    grade=self._sanitize_string(row['grade']) or "Please select an option",
                    score=max(0, int(row['score']) if row['score'] is not None else 0),
                    date_joined=date_joined,
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
        Fetch user's posts
        
        Args:
            user_id: User ID
            limit: Maximum number of posts to return
            
        Returns:
            List of PostData objects
        """
        try:
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
                    p.likes
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
                    post = PostData(
                        id=row['id'],
                        author_id=row['author_id'],
                        author_username=self._sanitize_string(row['author_username']),
                        caption=self._sanitize_string(row['caption']),
                        description=self._sanitize_string(row['description']),
                        likes=max(0, int(row['likes']) if row['likes'] is not None else 0)
                    )
                    posts.append(post)
                
                logger.info(f"Retrieved {len(posts)} posts for user {user_id}")
                return posts
                
        except Exception as e:
            logger.error(f"Error fetching user posts: {e}")
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
            user_id = self._validate_user_id(user_id)
            limit = self._validate_limit(limit)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    c.id,
                    c.author_id,
                    u.username as author_username,
                    c.body,
                    c.likes
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
                    comment = CommentData(
                        id=row['id'],
                        author_id=row['author_id'],
                        author_username=self._sanitize_string(row['author_username']),
                        body=self._sanitize_string(row['body']),
                        likes=max(0, int(row['likes']) if row['likes'] is not None else 0)
                    )
                    comments.append(comment)
                
                logger.info(f"Retrieved {len(comments)} comments for user {user_id}")
                return comments
                
        except Exception as e:
            logger.error(f"Error fetching user comments: {e}")
            return []

    def get_comprehensive_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get all available user data
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing all user data
        """
        profile = self.get_user_profile(user_id)
        posts = self.get_user_posts(user_id, 5)
        comments = self.get_user_comments(user_id, 5)
        
        return {
            "profile": profile.to_dict() if profile else None,
            "posts": [post.to_dict() for post in posts],
            "comments": [comment.to_dict() for comment in comments],
            "timestamp": datetime.now().isoformat()
        }

    def get_formatted_user_context(self, user_id: int) -> str:
        """
        Get formatted user context string for AI
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted string with user context
        """
        data = self.get_comprehensive_user_data(user_id)
        
        if not data["profile"]:
            return f"User {user_id} not found in database."
        
        profile = data["profile"]
        
        context = f"""
=== USER PROFILE ===
Name: {profile['first_name']} {profile['last_name']} (@{profile['username']})
Email: {profile['email']}
Grade Level: {profile['grade']}
Current Score: {profile['score']} points
Account Created: {profile['date_joined'][:10]}
Account Status: {'Active' if profile['is_active'] else 'Inactive'}

=== RECENT ACTIVITY ===
Recent Posts: {len(data['posts'])} posts
Recent Comments: {len(data['comments'])} comments
Platform Engagement: {'High' if len(data['posts']) + len(data['comments']) > 5 else 'Moderate' if len(data['posts']) + len(data['comments']) > 2 else 'Low'}

=== EDUCATIONAL CONTEXT ===
Grade Level: {profile['grade']}
Focus: {'Foundation building and core concepts' if 'Middle' in profile['grade'] else 'Advanced concepts and university preparation' if 'Senior' in profile['grade'] else 'General education'}
"""
        
        return context.strip()

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
            limit = self._validate_limit(limit)
            grade = self._sanitize_string(grade)
            
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
            logger.error(f"Error searching users by grade: {e}")
            return []

# Global instance for easy access
db_fetcher = DatabaseFetcher()

# Convenience functions
def get_user_profile(user_id: int) -> Optional[UserProfile]:
    """Get user profile - convenience function"""
    return db_fetcher.get_user_profile(user_id)

def get_user_context(user_id: int) -> str:
    """Get formatted user context - convenience function"""
    return db_fetcher.get_formatted_user_context(user_id)

def get_comprehensive_data(user_id: int) -> Dict[str, Any]:
    """Get all user data - convenience function"""
    return db_fetcher.get_comprehensive_user_data(user_id)

def get_user_posts(user_id: int, limit: int = 10) -> List[PostData]:
    """Get user posts - convenience function"""
    return db_fetcher.get_user_posts(user_id, limit)

def get_user_comments(user_id: int, limit: int = 10) -> List[CommentData]:
    """Get user comments - convenience function"""
    return db_fetcher.get_user_comments(user_id, limit)

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
