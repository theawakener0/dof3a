from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Student(models.Model):
    OPTION_SELECT = 'Please select an option'
    MIDDLE_ONE = 'Middle 1'
    MIDDLE_TWO = 'Middle 2'
    MIDDLE_THREE = 'Middle 3'

    SENIOR_ONE = 'Senior 1'
    SENIOR_TWO = 'Senior 2'
    SENIOR_THREE = 'Senior 3'

    STUDENT_GRADE = [
        (OPTION_SELECT, 'Please select an option'),
        (MIDDLE_ONE, 'Middle 1'),
        (MIDDLE_TWO, 'Middle 2'),
        (MIDDLE_THREE, 'Middle 3'),
        (SENIOR_ONE, 'Senior 1'),
        (SENIOR_TWO, 'Senior 2'),
        (SENIOR_THREE, 'Senior 3'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    grade = models.CharField(max_length=50, choices=STUDENT_GRADE, default=OPTION_SELECT)

# models.py

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.CharField(max_length=200)
    description = models.TextField()
    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.caption}, likes ({self.likes})'

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    likes = models.PositiveIntegerField(default=0)

# models.py

class StudyGroup(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_groups')
    topic = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

class StudyGroupInvite(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='invites')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='studygroup_invites')
    accepted = models.BooleanField(default=False)
    responded = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)