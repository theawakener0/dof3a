from django.shortcuts import render
from rest_framework import status, permissions, mixins, viewsets
from .serializers import StudentSerializer, PostSerializer
from .models import Student, Post

class StudentViewSet(mixins.RetrieveModelMixin, 
                     mixins.DestroyModelMixin, 
                     mixins.UpdateModelMixin, 
                     mixins.CreateModelMixin, 
                     viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()