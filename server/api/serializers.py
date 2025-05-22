from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from api.models import Comment, Post
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})

        if len(attrs['password']) < 8:
            raise serializers.ValidationError({'password': 'Password must be at least 8 characters long'})

        if not any(char.isdigit() for char in attrs['password']):
            raise serializers.ValidationError({'password': 'Password must contain at least one digit'})

        if not any(char.isalpha() for char in attrs['password']):
            raise serializers.ValidationError({'password': 'Password must contain at least one letter'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    like_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'like_count']
        read_only_fields = ['author', 'created_at']

    def get_like_count(self, obj):
        return obj.likes.count()
    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['author', 'created_at' , 'post']
    
