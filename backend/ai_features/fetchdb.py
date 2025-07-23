import os
import sys
import django
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to Python path so Django can find the dof3a module
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Use the existing Django settings instead of creating our own
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dof3a.settings.development')

# Setup Django
django.setup()
# Import Django models after setup
from django.contrib.auth import get_user_model
from dof3a_base.models import Student, Post, Comment, StudyGroup, StudyGroupInvite
from core.models import User

# Get the custom User model
User = get_user_model()

@dataclass
class UserProfile:
    """User profile data structure matching Django User model only"""
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    date_joined: datetime
    last_login: Optional[datetime]
    is_active: bool
    is_staff: bool
    is_superuser: bool
    
    def to_dict(self):
        data = asdict(self)
        data['date_joined'] = self.date_joined.isoformat()
        data['last_login'] = self.last_login.isoformat() if self.last_login else None
        return data

@dataclass
class StudentProfile:
    """Student profile data structure matching Django Student model"""
    user_id: int
    score: int
    grade: str
    
    def to_dict(self):
        return asdict(self)

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

@dataclass
class StudyGroupData:
    """Study group data structure matching Django models"""
    id: int
    host_id: int
    host_username: str
    topic: str
    location: str
    created_at: datetime
    scheduled_time: datetime
    is_active: bool
    
    def to_dict(self):
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['scheduled_time'] = self.scheduled_time.isoformat()
        return data

@dataclass
class StudyGroupInviteData:
    """Study group invite data structure matching Django models"""
    id: int
    group_id: int
    group_topic: str
    student_id: int
    student_username: str
    accepted: bool
    responded: bool
    notified: bool
    
    def to_dict(self):
        return asdict(self)

class DatabaseFetcher:
    """Database fetcher for the educational platform using Django ORM"""
    
    def __init__(self):
        """Initialize the database fetcher - Django handles connections"""
        pass
    
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
        Fetch user profile (authentication and basic info only)
        
        Args:
            user_id: User ID
            
        Returns:
            UserProfile object or None if not found
        """
        try:
            user_id = self._validate_user_id(user_id)
            
            # Get user data only
            user = User.objects.filter(id=user_id, is_active=True).first()
            if not user:
                logger.info(f"User with ID {user_id} not found or inactive")
                return None
            
            # Create UserProfile with only User model fields
            profile = UserProfile(
                user_id=user.id,
                username=self._sanitize_string(user.username) or f"user_{user_id}",
                email=self._sanitize_string(user.email) or "",
                first_name=self._sanitize_string(user.first_name) or "",
                last_name=self._sanitize_string(user.last_name) or "",
                date_joined=user.date_joined,
                last_login=user.last_login,
                is_active=user.is_active,
                is_staff=user.is_staff,
                is_superuser=user.is_superuser
            )
            
            logger.info(f"Successfully retrieved user profile for ID {user_id}")
            return profile
            
        except ValueError as e:
            logger.error(f"Validation error in get_user_profile: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_user_profile: {e}")
            raise Exception(f"Failed to fetch user profile: {e}")

    def get_student_profile(self, user_id: int) -> Optional[StudentProfile]:
        """
        Fetch student profile (educational data only)
        
        Args:
            user_id: User ID
            
        Returns:
            StudentProfile object or None if not found
        """
        try:
            user_id = self._validate_user_id(user_id)
            
            # Get student data
            try:
                student = Student.objects.select_related('user').get(user_id=user_id)
                
                profile = StudentProfile(
                    user_id=student.user.id,
                    score=max(0, int(student.score) if student.score is not None else 0),
                    grade=self._sanitize_string(student.grade) or "Please select an option"
                )
                
                logger.info(f"Successfully retrieved student profile for user ID {user_id}")
                return profile
                
            except Student.DoesNotExist:
                logger.info(f"Student profile not found for user ID {user_id}")
                return None
            
        except ValueError as e:
            logger.error(f"Validation error in get_student_profile: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_student_profile: {e}")
            raise Exception(f"Failed to fetch student profile: {e}")

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
            
            posts_qs = Post.objects.filter(author_id=user_id).select_related('author').order_by('-id')[:limit]
            
            posts = []
            for post in posts_qs:
                post_data = PostData(
                    id=post.id,
                    author_id=post.author.id,
                    author_username=self._sanitize_string(post.author.username),
                    caption=self._sanitize_string(post.caption),
                    description=self._sanitize_string(post.description),
                    likes=max(0, int(post.likes) if post.likes is not None else 0)
                )
                posts.append(post_data)
            
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
            
            # Prefetch liked_by to efficiently access the likes property
            comments_qs = Comment.objects.filter(author_id=user_id).select_related('author').prefetch_related('liked_by').order_by('-id')[:limit]
            
            comments = []
            for comment in comments_qs:
                comment_data = CommentData(
                    id=comment.id,
                    author_id=comment.author.id,
                    author_username=self._sanitize_string(comment.author.username),
                    body=self._sanitize_string(comment.body),
                    likes=max(0, comment.likes)  # comment.likes is a property that returns liked_by.count()
                )
                comments.append(comment_data)
            
            logger.info(f"Retrieved {len(comments)} comments for user {user_id}")
            return comments
            
        except Exception as e:
            if "no such column" in str(e) or "no such table" in str(e):
                logger.warning(f"Database schema incomplete for comments: {e}")
                return []
            logger.error(f"Error fetching user comments: {e}")
            return []

    def get_study_groups(self, user_id: int = None, limit: int = 10, active_only: bool = True) -> List[StudyGroupData]:
        """
        Fetch study groups (all or by host)
        
        Args:
            user_id: Host user ID (optional, if None returns all groups)
            limit: Maximum number of groups to return
            active_only: Only return active groups
            
        Returns:
            List of StudyGroupData objects
        """
        try:
            limit = self._validate_limit(limit)
            
            # Build query
            query = StudyGroup.objects.select_related('host')
            
            if user_id:
                user_id = self._validate_user_id(user_id)
                query = query.filter(host_id=user_id)
            
            if active_only:
                query = query.filter(is_active=True)
            
            groups_qs = query.order_by('-created_at')[:limit]
            
            groups = []
            for group in groups_qs:
                group_data = StudyGroupData(
                    id=group.id,
                    host_id=group.host.id,
                    host_username=self._sanitize_string(group.host.username),
                    topic=self._sanitize_string(group.topic),
                    location=self._sanitize_string(group.location),
                    created_at=group.created_at,
                    scheduled_time=group.scheduled_time,
                    is_active=group.is_active
                )
                groups.append(group_data)
            
            logger.info(f"Retrieved {len(groups)} study groups")
            return groups
            
        except Exception as e:
            if "no such column" in str(e) or "no such table" in str(e):
                logger.warning(f"Database schema incomplete for study groups: {e}")
                return []
            logger.error(f"Error fetching study groups: {e}")
            return []

    def get_study_group_invites(self, user_id: int, limit: int = 10) -> List[StudyGroupInviteData]:
        """
        Fetch study group invites for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of invites to return
            
        Returns:
            List of StudyGroupInviteData objects
        """
        try:
            user_id = self._validate_user_id(user_id)
            limit = self._validate_limit(limit)
            
            invites_qs = StudyGroupInvite.objects.filter(
                student_id=user_id
            ).select_related('group__host', 'student').order_by('-id')[:limit]
            
            invites = []
            for invite in invites_qs:
                invite_data = StudyGroupInviteData(
                    id=invite.id,
                    group_id=invite.group.id,
                    group_topic=self._sanitize_string(invite.group.topic),
                    student_id=invite.student.id,
                    student_username=self._sanitize_string(invite.student.username),
                    accepted=invite.accepted,
                    responded=invite.responded,
                    notified=invite.notified
                )
                invites.append(invite_data)
            
            logger.info(f"Retrieved {len(invites)} study group invites for user {user_id}")
            return invites
            
        except Exception as e:
            if "no such column" in str(e) or "no such table" in str(e):
                logger.warning(f"Database schema incomplete for study group invites: {e}")
                return []
            logger.error(f"Error fetching study group invites: {e}")
            return []

    def get_comprehensive_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get all available user data (separated user and student data)
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing all user data with separated concerns
        """
        user_profile = self.get_user_profile(user_id)
        student_profile = self.get_student_profile(user_id)
        posts = self.get_user_posts(user_id, 5)
        comments = self.get_user_comments(user_id, 5)
        study_groups = self.get_study_groups(user_id, 5)
        study_invites = self.get_study_group_invites(user_id, 5)
        
        return {
            "user_profile": user_profile.to_dict() if user_profile else None,
            "student_profile": student_profile.to_dict() if student_profile else None,
            "posts": [post.to_dict() for post in posts],
            "comments": [comment.to_dict() for comment in comments],
            "study_groups": [group.to_dict() for group in study_groups],
            "study_invites": [invite.to_dict() for invite in study_invites],
            "timestamp": datetime.now().isoformat()
        }

    def get_formatted_user_context(self, user_id: int) -> str:
        """
        Get formatted user context string for AI (with separated user/student data)
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted string with user context
        """
        data = self.get_comprehensive_user_data(user_id)
        
        if not data["user_profile"]:
            return f"User {user_id} not found in database."
        
        user_profile = data["user_profile"]
        student_profile = data["student_profile"]
        
        # Determine user type
        if user_profile['is_superuser']:
            user_type = "Administrator"
        elif user_profile['is_staff']:
            user_type = "Staff Member"
        elif student_profile:
            user_type = "Student"
        else:
            user_type = "Regular User"
        
        context = f"""
=== USER PROFILE ===
Name: {user_profile['first_name']} {user_profile['last_name']} (@{user_profile['username']})
Email: {user_profile['email']}
User Type: {user_type}
Account Created: {user_profile['date_joined'][:10]}
Last Login: {user_profile['last_login'][:10] if user_profile['last_login'] else 'Never'}
Account Status: {'Active' if user_profile['is_active'] else 'Inactive'}"""
        
        # Add student-specific information if available
        if student_profile:
            context += f"""

=== STUDENT PROFILE ===
Grade Level: {student_profile['grade']}
Current Score: {student_profile['score']} points
Academic Focus: {'Foundation building and core concepts' if 'Middle' in student_profile['grade'] else 'Advanced concepts and university preparation' if 'Senior' in student_profile['grade'] else 'General education'}"""
        
        context += f"""

=== RECENT ACTIVITY ===
Recent Posts: {len(data['posts'])} posts
Recent Comments: {len(data['comments'])} comments
Study Groups Hosted: {len(data['study_groups'])} groups
Study Group Invites: {len(data['study_invites'])} invites
Platform Engagement: {'High' if len(data['posts']) + len(data['comments']) + len(data['study_groups']) > 7 else 'Moderate' if len(data['posts']) + len(data['comments']) + len(data['study_groups']) > 3 else 'Low'}"""
        
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
            
            students = Student.objects.filter(grade=grade, user__is_active=True).select_related('user').order_by('-score')[:limit]
            
            users = []
            for student in students:
                users.append({
                    'id': student.user.id,
                    'username': student.user.username,
                    'first_name': student.user.first_name,
                    'last_name': student.user.last_name,
                    'score': student.score,
                    'grade': student.grade
                })
            
            return users
            
        except Exception as e:
            logger.error(f"Error searching users by grade: {e}")
            return []

# Global instance for easy access
db_fetcher = DatabaseFetcher()

# Convenience functions
def get_user_profile(user_id: int) -> Optional[UserProfile]:
    """Get user profile (authentication data only) - convenience function"""
    return db_fetcher.get_user_profile(user_id)

def get_student_profile(user_id: int) -> Optional[StudentProfile]:
    """Get student profile (educational data only) - convenience function"""
    return db_fetcher.get_student_profile(user_id)

def get_user_context(user_id: int) -> str:
    """Get formatted user context - convenience function"""
    return db_fetcher.get_formatted_user_context(user_id)

def get_comprehensive_data(user_id: int) -> Dict[str, Any]:
    """Get all user data (separated user/student) - convenience function"""
    return db_fetcher.get_comprehensive_user_data(user_id)

def get_user_posts(user_id: int, limit: int = 10) -> List[PostData]:
    """Get user posts - convenience function"""
    return db_fetcher.get_user_posts(user_id, limit)

def get_user_comments(user_id: int, limit: int = 10) -> List[CommentData]:
    """Get user comments - convenience function"""
    return db_fetcher.get_user_comments(user_id, limit)

def get_study_groups(user_id: int = None, limit: int = 10, active_only: bool = True) -> List[StudyGroupData]:
    """Get study groups - convenience function"""
    return db_fetcher.get_study_groups(user_id, limit, active_only)

def get_study_group_invites(user_id: int, limit: int = 10) -> List[StudyGroupInviteData]:
    """Get study group invites - convenience function"""
    return db_fetcher.get_study_group_invites(user_id, limit)

# Django ORM based functions matching the requested code structure

def fetch_all_users():
    """Fetches and prints all users."""
    print("\n--- All Users ---")
    users = User.objects.all()
    if not users:
        print("No users found.")
        return
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

def fetch_student_data(username=None, grade=None, top_n=None):
    """
    Fetches and prints student data based on criteria.
    Args:
        username (str, optional): Fetch student by username.
        grade (str, optional): Fetch students by grade.
        top_n (int, optional): Fetch top N students by score.
    """
    print("\n--- Student Data ---")
    if username:
        try:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            print(f"Student: {student.user.username}, Grade: {student.grade}, Score: {student.score}")
        except User.DoesNotExist:
            print(f"User '{username}' not found.")
        except Student.DoesNotExist:
            print(f"Student profile for '{username}' not found.")
    elif grade:
        students = Student.objects.filter(grade=grade).select_related('user')
        if not students:
            print(f"No students found in grade '{grade}'.")
            return
        print(f"Students in grade '{grade}':")
        for student in students:
            print(f"  {student.user.username}, Score: {student.score}")
    elif top_n:
        students = Student.objects.all().select_related('user').order_by('-score')[:top_n]
        if not students:
            print(f"No students found (top {top_n}).")
            return
        print(f"Top {top_n} students by score:")
        for student in students:
            print(f"  {student.user.username}, Score: {student.score}, Grade: {student.grade}")
    else:
        students = Student.objects.all().select_related('user')
        if not students:
            print("No students found.")
            return
        print("All students:")
        for student in students:
            print(f"  {student.user.username}, Grade: {student.grade}, Score: {student.score}")

def fetch_post_data(author_username=None, post_id=None, recent_n=None):
    """
    Fetches and prints post data based on criteria.
    Args:
        author_username (str, optional): Fetch posts by author's username.
        post_id (int, optional): Fetch a specific post by ID.
        recent_n (int, optional): Fetch N most recent posts.
    """
    print("\n--- Post Data ---")
    if post_id:
        try:
            post = Post.objects.get(id=post_id)
            print(f"Post ID: {post.id}")
            print(f"  Author: {post.author.username}")
            print(f"  Caption: {post.caption}")
            print(f"  Description: {post.description}")
            print(f"  Likes: {post.likes}")
        except Post.DoesNotExist:
            print(f"Post with ID {post_id} not found.")
    elif author_username:
        try:
            author = User.objects.get(username=author_username)
            posts = Post.objects.filter(author=author)
            if not posts:
                print(f"No posts found for author '{author_username}'.")
                return
            print(f"Posts by '{author_username}':")
            for post in posts:
                print(f"  - '{post.caption}' (Likes: {post.likes})")
        except User.DoesNotExist:
            print(f"Author '{author_username}' not found.")
    elif recent_n:
        posts = Post.objects.all().select_related('author').order_by('-id')[:recent_n]
        if not posts:
            print(f"No recent posts found (top {recent_n}).")
            return
        print(f"Most recent {recent_n} posts:")
        for post in posts:
            print(f"  - '{post.caption}' by {post.author.username} (Likes: {post.likes})")
    else:
        posts = Post.objects.all().select_related('author')
        if not posts:
            print("No posts found.")
            return
        print("All posts:")
        for post in posts:
            print(f"  - '{post.caption}' by {post.author.username} (Likes: {post.likes})")

def fetch_comment_data(post_id=None, author_username=None):
    """
    Fetches and prints comment data based on criteria.
    Args:
        post_id (int, optional): Fetch comments for a specific post ID.
        author_username (str, optional): Fetch comments by a specific author's username.
    """
    print("\n--- Comment Data ---")
    if post_id:
        try:
            post = Post.objects.get(id=post_id)
            comments = Comment.objects.filter(post=post).select_related('author').prefetch_related('liked_by')
            if not comments:
                print(f"No comments found for post ID {post_id}.")
                return
            print(f"Comments for post '{post.caption}':")
            for comment in comments:
                print(f"  - By {comment.author.username}: '{comment.body}' (Likes: {comment.likes})")
        except Post.DoesNotExist:
            print(f"Post with ID {post_id} not found.")
    elif author_username:
        try:
            author = User.objects.get(username=author_username)
            comments = Comment.objects.filter(author=author).select_related('post').prefetch_related('liked_by')
            if not comments:
                print(f"No comments found by '{author_username}'.")
                return
            print(f"Comments by '{author_username}':")
            for comment in comments:
                print(f"  - On '{comment.post.caption[:20]}...': '{comment.body}' (Likes: {comment.likes})")
        except User.DoesNotExist:
            print(f"Author '{author_username}' not found.")
    else:
        comments = Comment.objects.all().select_related('author', 'post').prefetch_related('liked_by')
        if not comments:
            print("No comments found.")
            return
        print("All comments:")
        for comment in comments:
            print(f"  - By {comment.author.username} on '{comment.post.caption[:20]}...': '{comment.body}' (Likes: {comment.likes})")

def fetch_study_group_data(group_id=None, host_username=None, topic=None, active_only=False):
    """
    Fetches and prints study group data based on criteria.
    Args:
        group_id (int, optional): Fetch a specific study group by ID.
        host_username (str, optional): Fetch groups hosted by a specific user.
        topic (str, optional): Fetch groups by topic.
        active_only (bool, optional): Fetch only active groups.
    """
    print("\n--- Study Group Data ---")
    if group_id:
        try:
            group = StudyGroup.objects.get(id=group_id)
            print(f"Study Group ID: {group.id}")
            print(f"  Topic: {group.topic}")
            print(f"  Host: {group.host.username}")
            print(f"  Location: {group.location}")
            print(f"  Created: {group.created_at}")
            print(f"  Scheduled: {group.scheduled_time}")
            print(f"  Active: {group.is_active}")
        except StudyGroup.DoesNotExist:
            print(f"Study Group with ID {group_id} not found.")
    elif host_username:
        try:
            host = User.objects.get(username=host_username)
            groups = StudyGroup.objects.filter(host=host)
            if not groups:
                print(f"No study groups hosted by '{host_username}'.")
                return
            print(f"Study Groups hosted by '{host_username}':")
            for group in groups:
                print(f"  - '{group.topic}' at {group.location} (Active: {group.is_active})")
        except User.DoesNotExist:
            print(f"Host '{host_username}' not found.")
    elif topic:
        groups = StudyGroup.objects.filter(topic__icontains=topic).select_related('host')
        if not groups:
            print(f"No study groups found for topic '{topic}'.")
            return
        print(f"Study Groups related to topic '{topic}':")
        for group in groups:
            print(f"  - '{group.topic}' by {group.host.username} at {group.location}")
    elif active_only:
        groups = StudyGroup.objects.filter(is_active=True).select_related('host')
        if not groups:
            print("No active study groups found.")
            return
        print("Active Study Groups:")
        for group in groups:
            print(f"  - '{group.topic}' by {group.host.username} at {group.location}")
    else:
        groups = StudyGroup.objects.all().select_related('host')
        if not groups:
            print("No study groups found.")
            return
        print("All Study Groups:")
        for group in groups:
            print(f"  - '{group.topic}' by {group.host.username} (Active: {group.is_active})")

def fetch_study_group_invite_data(user_username=None, group_id=None, pending_only=False, accepted_only=False):
    """
    Fetches and prints study group invite data based on criteria.
    Args:
        user_username (str, optional): Fetch invites for a specific user.
        group_id (int, optional): Fetch invites for a specific group.
        pending_only (bool, optional): Fetch only pending invites for a user.
        accepted_only (bool, optional): Fetch only accepted invites for a group.
    """
    print("\n--- Study Group Invite Data ---")
    if user_username and pending_only:
        try:
            user = User.objects.get(username=user_username)
            invites = StudyGroupInvite.objects.filter(student=user, responded=False).select_related('group__host')
            if not invites:
                print(f"No pending invites for user '{user_username}'.")
                return
            print(f"Pending Invites for '{user_username}':")
            for invite in invites:
                print(f"  - To group '{invite.group.topic}' (Host: {invite.group.host.username})")
        except User.DoesNotExist:
            print(f"User '{user_username}' not found.")
    elif group_id and accepted_only:
        try:
            group = StudyGroup.objects.get(id=group_id)
            invites = StudyGroupInvite.objects.filter(group=group, accepted=True).select_related('student')
            if not invites:
                print(f"No accepted invites for group ID {group_id}.")
                return
            print(f"Accepted Invites for group '{group.topic}':")
            for invite in invites:
                print(f"  - For student '{invite.student.username}'")
        except StudyGroup.DoesNotExist:
            print(f"Study Group with ID {group_id} not found.")
    elif user_username:
        try:
            user = User.objects.get(username=user_username)
            invites = StudyGroupInvite.objects.filter(student=user).select_related('group__host')
            if not invites:
                print(f"No invites found for user '{user_username}'.")
                return
            print(f"All Invites for '{user_username}':")
            for invite in invites:
                status = "Accepted" if invite.accepted else ("Responded" if invite.responded else "Pending")
                print(f"  - To group '{invite.group.topic}' (Status: {status})")
        except User.DoesNotExist:
            print(f"User '{user_username}' not found.")
    elif group_id:
        try:
            group = StudyGroup.objects.get(id=group_id)
            invites = StudyGroupInvite.objects.filter(group=group).select_related('student')
            if not invites:
                print(f"No invites found for group ID {group_id}.")
                return
            print(f"All Invites for group '{group.topic}':")
            for invite in invites:
                status = "Accepted" if invite.accepted else ("Responded" if invite.responded else "Pending")
                print(f"  - For student '{invite.student.username}' (Status: {status})")
        except StudyGroup.DoesNotExist:
            print(f"Study Group with ID {group_id} not found.")
    else:
        invites = StudyGroupInvite.objects.all().select_related('group__host', 'student')
        if not invites:
            print("No study group invites found.")
            return
        print("All Study Group Invites:")
        for invite in invites:
            status = "Accepted" if invite.accepted else ("Responded" if invite.responded else "Pending")
            print(f"  - From '{invite.group.host.username}' to '{invite.student.username}' for '{invite.group.topic}' (Status: {status})")

# Test function
def test_database_connection():
    """Test database connection and fetch sample data"""
    try:
        # Test with user ID 1
        user_profile = get_user_profile(1)
        student_profile = get_student_profile(1)
        
        if user_profile:
            print("✅ Database connection successful!")
            print(f"Sample user: {user_profile.username} (Email: {user_profile.email})")
            
            if student_profile:
                print(f"Student data: Grade {student_profile.grade}, Score {student_profile.score}")
            else:
                print("No student profile found for this user")
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
        
    # Example of using the fetch functions
    print("\n=== DEMO FUNCTIONS ===")
    fetch_all_users()
    fetch_student_data(top_n=3)
    fetch_post_data(recent_n=3)
