from django.shortcuts import render
from rest_framework import status, permissions, mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import StudentSerializer, PostSerializer, CreatePostSerialier, CommentSerializer, FriendRequestSerializer
from .models import Student, Post, Comment, FriendRequest
from .permissions.comment_perms import IsCommentAuthor

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

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
        
    @action(detail=True, methods=['GET'], url_path='send_friend_request')
    def send_friend_request(self, request, pk=None):
        try:
            current_user = request.user
            target_user = Student.objects.get(pk=pk)

            if current_user.student == target_user:
                return Response({'error': 'You cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

            (friend_request, created) = FriendRequest.objects.get_or_create(
                from_student=current_user.student,
                to_student=target_user
            )

            if created:
                return Response({'success': 'Friend request sent.'}, status=status.HTTP_200_OK)
            else:
                return Response({'info': 'Friend request already sent.'}, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response({'error': 'Target student not found'}, status=status.HTTP_404_NOT_FOUND)
        
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


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        current_student = self.request.user.student
        return FriendRequest.objects.filter(to_student=current_student)

    @action(detail=True, methods=['POST', 'GET'], url_path='accept')
    def accept_request(self, request, pk=None):
        try:
            current_student = request.user.student
            friend_request = FriendRequest.objects.get(pk=pk)

            if friend_request.to_student != current_student:
                return Response({'error': 'Unauthorized action.'}, status=status.HTTP_403_FORBIDDEN)

            current_student.friends.add(friend_request.from_student)
            friend_request.from_student.friends.add(current_student)

            friend_request.delete()

            return Response({'success': 'Friend request accepted.'}, status=status.HTTP_200_OK)

        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['POST', 'GET'], url_path='reject')
    def reject_request(self, request, pk=None):
        try:
            friend_request = FriendRequest.objects.get(pk=pk)
            current_student = request.user.student

            if friend_request.to_student != current_student:
                return Response({'error': 'Unauthorized action.'}, status=status.HTTP_403_FORBIDDEN)

            friend_request.delete()
            return Response({'success': 'Friend request rejected.'}, status=status.HTTP_200_OK)

        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)