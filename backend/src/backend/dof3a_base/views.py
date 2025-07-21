from django.shortcuts import render
from rest_framework import status, permissions, mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import StudentSerializer, PostSerializer, CreatePostSerialier, CommentSerializer
from .models import Student, Post, Comment
from .permissions.comment_perms import IsCommentAuthor

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['GET'], url_path='my_profile')
    def my_profile(self, request):
        try:
            user_id = request.user.id
            user = Student.objects.get(user=user_id)
            if request.method == 'GET':
                serializer = StudentSerializer(user)
                return Response(serializer.data)
            elif request.method == 'PUT':
                serializer = StudentSerializer(user, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'detail': 'No user found with this ID.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostSerializer
        return CreatePostSerialier
    
    def get_serializer_context(self):
        return {'author': self.request.user}

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsCommentAuthor()]

    def get_queryset(self):
        post_pk = self.kwargs['post_pk']
        return Comment.objects.filter(post=post_pk)
    
    def get_serializer_context(self):
        return {
            'author': self.request.user,
            'post': self.kwargs['post_pk']
                }

    @action(detail=True, methods=['POST', 'GET'], permission_classes=[IsCommentAuthor, permissions.IsAuthenticated])
    def like_comment(self, request, *args, **kwargs):
        comment_id = kwargs.get('pk')
        post_id = kwargs.get('post_pk')
        user = request.user

        try:
            comment = Comment.objects.get(id=comment_id, post_id=post_id)
            if comment.liked_by.filter(id=user.id).exists():
                return Response({'detail': 'You already liked this comment.'}, status=status.HTTP_400_BAD_REQUEST)
            comment.liked_by.add(user)
            return Response({'likes': comment.likes}, status=status.HTTP_200_OK)
        
        except Comment.DoesNotExist:
            return Response({'detail': 'No comment found with this ID.'}, status=status.HTTP_404_NOT_FOUND)
