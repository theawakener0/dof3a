# Enhanced Models Structure for Educational Platform
# This shows the recommended database structure that should be added to Django models

"""
Recommended additional models to add to dof3a_base/models.py:

1. KNOCKOUT GAME MODELS
"""

# class Subject(models.Model):
#     """Subject categories for the educational platform"""
#     SUBJECT_CHOICES = [
#         ('math', 'Mathematics'),
#         ('physics', 'Physics'),
#         ('chemistry', 'Chemistry'),
#         ('biology', 'Biology'),
#         ('arabic', 'Arabic Language'),
#         ('english', 'English Language'),
#         ('science', 'General Science'),
#         ('social_studies', 'Social Studies'),
#         ('history', 'History'),
#         ('geography', 'Geography'),
#     ]
    
#     name = models.CharField(max_length=50, choices=SUBJECT_CHOICES, unique=True)
#     display_name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     grade_levels = models.JSONField(default=list)  # List of applicable grade levels
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return self.display_name

# class KnockoutGame(models.Model):
#     """1v1 Knockout game records"""
#     DIFFICULTY_CHOICES = [
#         ('easy', 'Easy'),
#         ('medium', 'Medium'),
#         ('hard', 'Hard'),
#     ]
    
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('in_progress', 'In Progress'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     ]
    
#     # Game participants
#     player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='knockout_player1')
#     player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='knockout_player2')
    
#     # Game details
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
#     status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
#     # Scores
#     player1_score = models.PositiveIntegerField(default=0)
#     player2_score = models.PositiveIntegerField(default=0)
#     winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='knockout_wins')
    
#     # Points awarded
#     points_awarded = models.PositiveIntegerField(default=0)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     started_at = models.DateTimeField(null=True, blank=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
    
#     # Game settings
#     total_questions = models.PositiveIntegerField(default=10)
#     time_limit_seconds = models.PositiveIntegerField(default=300)  # 5 minutes default
    
#     def __str__(self):
#         return f"{self.player1.username} vs {self.player2.username} - {self.subject.display_name}"

# class KnockoutQuestion(models.Model):
#     """Individual questions for knockout games"""
#     game = models.ForeignKey(KnockoutGame, on_delete=models.CASCADE, related_name='questions')
#     question_text = models.TextField()
#     option_a = models.CharField(max_length=200)
#     option_b = models.CharField(max_length=200)
#     option_c = models.CharField(max_length=200)
#     option_d = models.CharField(max_length=200)
#     correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
#     explanation = models.TextField(blank=True)
#     difficulty_score = models.PositiveIntegerField(default=5)  # 1-10 scale
#     estimated_time_seconds = models.PositiveIntegerField(default=30)
#     question_order = models.PositiveIntegerField()
    
#     class Meta:
#         ordering = ['question_order']

# class KnockoutAnswer(models.Model):
#     """User answers for knockout questions"""
#     question = models.ForeignKey(KnockoutQuestion, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     selected_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
#     is_correct = models.BooleanField()
#     time_taken_seconds = models.PositiveIntegerField()
#     answered_at = models.DateTimeField(auto_now_add=True)

# """
# 2. STUDY GROUP MODELS
# """

# class StudyGroup(models.Model):
#     """Study groups for collaborative learning"""
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     grade_level = models.CharField(max_length=50, choices=Student.STUDENT_GRADE)
    
#     # Group settings
#     max_members = models.PositiveIntegerField(default=8)
#     is_private = models.BooleanField(default=False)
#     requires_approval = models.BooleanField(default=False)
    
#     # Location and schedule
#     meeting_location = models.CharField(max_length=200, blank=True)
#     meeting_schedule = models.TextField(blank=True)  # JSON or text description
    
#     # Admin
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_study_groups')
#     admins = models.ManyToManyField(User, related_name='admin_study_groups', blank=True)
#     members = models.ManyToManyField(User, through='StudyGroupMembership', related_name='study_groups')
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.name} - {self.subject.display_name} ({self.grade_level})"

# class StudyGroupMembership(models.Model):
#     """Membership in study groups"""
#     ROLE_CHOICES = [
#         ('member', 'Member'),
#         ('admin', 'Admin'),
#         ('moderator', 'Moderator'),
#     ]
    
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('active', 'Active'),
#         ('inactive', 'Inactive'),
#         ('banned', 'Banned'),
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
#     joined_at = models.DateTimeField(auto_now_add=True)
#     last_active = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ['user', 'study_group']

# """
# 3. COURSE PROGRESS MODELS
# """

# class CourseProgress(models.Model):
#     """Track student progress in different subjects"""
#     student = models.ForeignKey(User, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     grade_level = models.CharField(max_length=50, choices=Student.STUDENT_GRADE)
    
#     # Progress metrics
#     current_score = models.FloatField(default=0.0)
#     total_questions_attempted = models.PositiveIntegerField(default=0)
#     correct_answers = models.PositiveIntegerField(default=0)
#     incorrect_answers = models.PositiveIntegerField(default=0)
    
#     # Calculated fields
#     accuracy_percentage = models.FloatField(default=0.0)
#     time_spent_minutes = models.PositiveIntegerField(default=0)
#     improvement_rate = models.FloatField(default=0.0)  # Percentage improvement
    
#     # Difficulty tracking
#     difficulty_level = models.CharField(max_length=10, choices=[
#         ('easy', 'Easy'),
#         ('medium', 'Medium'),
#         ('hard', 'Hard'),
#     ], default='medium')
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     last_activity = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ['student', 'subject', 'grade_level']
        
#     def update_accuracy(self):
#         """Update accuracy percentage based on answers"""
#         if self.total_questions_attempted > 0:
#             self.accuracy_percentage = (self.correct_answers / self.total_questions_attempted) * 100
#         else:
#             self.accuracy_percentage = 0.0
#         self.save()

# class QuizSession(models.Model):
#     """Individual quiz sessions for tracking detailed progress"""
#     student = models.ForeignKey(User, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     course_progress = models.ForeignKey(CourseProgress, on_delete=models.CASCADE)
    
#     # Session details
#     session_name = models.CharField(max_length=100, blank=True)
#     total_questions = models.PositiveIntegerField()
#     correct_answers = models.PositiveIntegerField()
#     score_percentage = models.FloatField()
#     time_taken_minutes = models.PositiveIntegerField()
#     difficulty = models.CharField(max_length=10, choices=[
#         ('easy', 'Easy'),
#         ('medium', 'Medium'),
#         ('hard', 'Hard'),
#     ])
    
#     # Timestamps
#     started_at = models.DateTimeField()
#     completed_at = models.DateTimeField()
#     created_at = models.DateTimeField(auto_now_add=True)

# """
# 4. SCHOOL GROUP MODELS
# """

# class School(models.Model):
#     """Schools for organizing students"""
#     name = models.CharField(max_length=200)
#     code = models.CharField(max_length=20, unique=True)  # School identifier
#     address = models.TextField(blank=True)
#     city = models.CharField(max_length=100)
#     governorate = models.CharField(max_length=100)  # Egyptian governorates
    
#     # Contact info
#     phone = models.CharField(max_length=20, blank=True)
#     email = models.EmailField(blank=True)
#     website = models.URLField(blank=True)
    
#     # Settings
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.name} ({self.code})"

# class SchoolGroup(models.Model):
#     """School-specific groups that only students from that school can join"""
#     school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='groups')
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     grade_levels = models.JSONField(default=list)  # List of grade levels allowed
    
#     # Group settings
#     is_active = models.BooleanField(default=True)
#     max_members = models.PositiveIntegerField(default=50)
    
#     # Admin
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     moderators = models.ManyToManyField(User, related_name='moderated_school_groups', blank=True)
#     members = models.ManyToManyField(User, related_name='school_groups', blank=True)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.school.name} - {self.name}"

# """
# 5. ENHANCED POST AND COMMENT MODELS
# """

# # Update existing Post model to include:
# class EnhancedPost(models.Model):
#     """Enhanced post model with more fields"""
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     caption = models.CharField(max_length=200)
#     description = models.TextField()
    
#     # Content type
#     POST_TYPES = [
#         ('text', 'Text Post'),
#         ('image', 'Image Post'),
#         ('video', 'Video Post'),
#         ('reel', 'Educational Reel'),
#         ('question', 'Question Post'),
#         ('resource', 'Learning Resource'),
#     ]
#     post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    
#     # Educational categorization
#     subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
#     grade_levels = models.JSONField(default=list)  # Target grade levels
    
#     # Engagement
#     likes = models.PositiveIntegerField(default=0)
#     views = models.PositiveIntegerField(default=0)
#     shares = models.PositiveIntegerField(default=0)
    
#     # Moderation
#     is_approved = models.BooleanField(default=False)
#     moderation_score = models.FloatField(default=0.0)
#     is_educational = models.BooleanField(default=True)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f'{self.caption} by {self.author.username}'

# # Update existing Comment model to include:
# class EnhancedComment(models.Model):
#     """Enhanced comment model"""
#     post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # For replies
#     body = models.TextField()
#     likes = models.PositiveIntegerField(default=0)
    
#     # Moderation
#     is_approved = models.BooleanField(default=True)
#     is_helpful = models.BooleanField(default=False)  # Marked by post author
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f'Comment by {self.author.username} on {self.post.caption[:30]}'

# """
# 6. ANALYTICS AND TRACKING MODELS
# """

# class UserActivity(models.Model):
#     """Track user activities for analytics"""
#     ACTIVITY_TYPES = [
#         ('login', 'Login'),
#         ('logout', 'Logout'),
#         ('post_create', 'Post Created'),
#         ('comment_create', 'Comment Created'),
#         ('knockout_join', 'Joined Knockout'),
#         ('knockout_complete', 'Completed Knockout'),
#         ('study_session', 'Study Session'),
#         ('quiz_complete', 'Quiz Completed'),
#         ('group_join', 'Joined Study Group'),
#         ('profile_update', 'Profile Updated'),
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
#     description = models.TextField(blank=True)
    
#     # Additional data (JSON for flexibility)
#     metadata = models.JSONField(default=dict, blank=True)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-created_at']

# class LearningStreak(models.Model):
#     """Track learning streaks for gamification"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     current_streak = models.PositiveIntegerField(default=0)
#     longest_streak = models.PositiveIntegerField(default=0)
#     last_activity_date = models.DateField(auto_now_add=True)
    
#     def update_streak(self):
#         """Update streak based on activity"""
#         from django.utils import timezone
#         today = timezone.now().date()
        
#         if self.last_activity_date == today:
#             # Already active today, no change
#             return
#         elif self.last_activity_date == today - timezone.timedelta(days=1):
#             # Consecutive day, increment streak
#             self.current_streak += 1
#             if self.current_streak > self.longest_streak:
#                 self.longest_streak = self.current_streak
#         else:
#             # Streak broken, reset
#             self.current_streak = 1
        
#         self.last_activity_date = today
#         self.save()

# """
# 7. UPDATE EXISTING STUDENT MODEL
# """

# # Enhanced Student model (to replace existing):
# class EnhancedStudent(models.Model):
#     OPTION_SELECT = 'Please select an option'
#     MIDDLE_ONE = 'Middle 1'
#     MIDDLE_TWO = 'Middle 2'
#     MIDDLE_THREE = 'Middle 3'
#     SENIOR_ONE = 'Senior 1'
#     SENIOR_TWO = 'Senior 2'
#     SENIOR_THREE = 'Senior 3'

#     STUDENT_GRADE = [
#         (OPTION_SELECT, 'Please select an option'),
#         (MIDDLE_ONE, 'Middle 1'),
#         (MIDDLE_TWO, 'Middle 2'),
#         (MIDDLE_THREE, 'Middle 3'),
#         (SENIOR_ONE, 'Senior 1'),
#         (SENIOR_TWO, 'Senior 2'),
#         (SENIOR_THREE, 'Senior 3'),
#     ]

#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     score = models.PositiveIntegerField(default=0)
#     grade = models.CharField(max_length=50, choices=STUDENT_GRADE, default=OPTION_SELECT)
    
#     # Additional profile fields
#     school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
#     bio = models.TextField(blank=True, max_length=500)
#     profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
#     # Learning preferences
#     learning_style = models.CharField(max_length=20, choices=[
#         ('visual', 'Visual'),
#         ('auditory', 'Auditory'),
#         ('kinesthetic', 'Kinesthetic'),
#         ('mixed', 'Mixed'),
#     ], default='mixed')
    
#     study_hours_per_day = models.PositiveIntegerField(default=2)
#     preferred_subjects = models.ManyToManyField(Subject, blank=True)
    
#     # Goals and aspirations
#     target_universities = models.JSONField(default=list, blank=True)
#     career_interests = models.JSONField(default=list, blank=True)
    
#     # Privacy settings
#     profile_visibility = models.CharField(max_length=10, choices=[
#         ('public', 'Public'),
#         ('friends', 'Friends Only'),
#         ('private', 'Private'),
#     ], default='public')
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.user.username} - {self.grade}"
