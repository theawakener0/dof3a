from django.shortcuts import render
from rest_framework import status, permissions, mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import StudentSerializer, PostSerializer, CreatePostSerialier, CommentSerializer
from .models import Student, Post, Comment, StudyGroupInvite, StudyGroup

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'], url_path='my_profile')
    def my_profile(self, request):
        user_pk = request.user.id

        try:
            student = Student.objects.get(user__id=user_pk)
        except Student.DoesNotExist:
            return Response({'detail': 'No student exists for this user.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method in ['PUT', 'PATCH']:
            serializer = StudentSerializer(
                student,
                data=request.data,
                partial=(request.method == 'PATCH'),
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentSerializer(student, context={'request': request})
        return Response(serializer.data)
        
class PostViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostSerializer
        return CreatePostSerialier
    
    def get_serializer_context(self):
        return {'author': self.request.user}
    
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class CommentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        post_pk = self.kwargs['post_pk']
        return Comment.objects.filter(post=post_pk)
    
    serializer_class = CommentSerializer
    
    def get_serializer_context(self):
        return {
            'author': self.request.user,
            'post': self.kwargs['post_pk']
                }
    permission_classes = [permissions.IsAuthenticated]