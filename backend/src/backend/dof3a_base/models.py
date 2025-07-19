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

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    likes = models.PositiveIntegerField()

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.CharField(max_length=200)
    description = models.TextField()
    likes = models.PositiveIntegerField()
    comments = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.caption}, likes ({self.likes})'