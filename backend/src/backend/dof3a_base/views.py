from django.shortcuts import render
from rest_framework import status, permissions, mixins, viewsets
from .serializers import StudentSerializer
from .models import Student

class StudentViewSet(mixins.RetrieveModelMixin, 
                     mixins.DestroyModelMixin, 
                     mixins.UpdateModelMixin, 
                     mixins.CreateModelMixin, 
                     viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()