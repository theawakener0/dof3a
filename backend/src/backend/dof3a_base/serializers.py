from rest_framework import serializers
from .models import Student, Post, Comment, StudyGroup, StudyGroupInvite

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'grade', 'score']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH']:
            for field_name in self.fields:
                if field_name != 'grade':
                    self.fields[field_name].read_only = True

class SimpleCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'body', 'likes']

class PostSerializer(serializers.ModelSerializer):
    comments = SimpleCommentSerializer(many=True)
    class Meta:
        model = Post
        fields = ['id', 'author', 'caption', 'description', 'comments']

class CreatePostSerialier(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['caption', 'description']

    def create(self, validated_data):
        author = self.context.get('author')
        validated_data['author'] = author
        return super().create(validated_data)
    
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'body', 'likes']
        read_only_fields = ['id', 'author', 'post', 'likes']

    def create(self, validated_data):
        author = self.context.get('author')
        post_pk = self.context.get('post')
        post = Post.objects.get(pk=post_pk)

        validated_data['author'] = author
        validated_data['post'] = post
        validated_data['likes'] = 0

        return super().create(validated_data)