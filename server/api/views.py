from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status , permissions 
from django.contrib.auth.models import User
from api.serializers import CommentSerializer, NotificationSerializer, PostSerializer, RegisterSerializer, UserProfileSerializer, UserProfileUpdateSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.models import Comment, Follow, Notification, Post, UserProfile
from api.permissions import IsAuthorOrReadOnly

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self , request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self , request) : 
        try : 
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e :
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class PostListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self , request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts , many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self , request):
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostRetrieveUpdateDestroyView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user in post.likes.all():
            return Response({'detail': 'You already liked this post.'}, status=status.HTTP_400_BAD_REQUEST)
        post.likes.add(request.user)
        return Response({'detail': 'Post liked.'}, status=status.HTTP_201_CREATED)


class UnlikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user not in post.likes.all():
            return Response({'detail': 'You have not liked this post.'}, status=status.HTTP_400_BAD_REQUEST)

        post.likes.remove(request.user)
        return Response({'detail': 'Post unliked.'}, status=status.HTTP_200_OK)
    

class PostCommentsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        return comment

    def get(self, request, post_id, comment_id):
        comment = self.get_object(post_id, comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, post_id, comment_id):
        comment = self.get_object(post_id, comment_id)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, comment_id):
        comment = self.get_object(post_id, comment_id)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileUpdateSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        
        # Получаем или создаем профиль, если его нет
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user, bio='', avatar=None)
        
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

class UserPostsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        posts = Post.objects.filter(author=user).order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, username):
        user_to_follow = get_object_or_404(User, username=username)
        
        if user_to_follow == request.user:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if not created:
            return Response({'detail': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Создание уведомления
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            notification_type='follow'
        )
        
        return Response({'detail': 'Successfully followed user.'}, status=status.HTTP_201_CREATED)

class UnfollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, username):
        user_to_unfollow = get_object_or_404(User, username=username)
        
        try:
            follow = Follow.objects.get(follower=request.user, following=user_to_unfollow)
            follow.delete()
            return Response({'detail': 'Successfully unfollowed user.'}, status=status.HTTP_200_OK)
        except Follow.DoesNotExist:
            return Response({'detail': 'You are not following this user.'}, status=status.HTTP_400_BAD_REQUEST)

class UserFollowersView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        followers = User.objects.filter(following__following=user)
        serializer = UserSerializer(followers, many=True, context={'request': request})
        return Response(serializer.data)

class UserFollowingView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        following = User.objects.filter(followers__follower=user)
        serializer = UserSerializer(following, many=True, context={'request': request})
        return Response(serializer.data)

class FeedView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Получаем пользователей, на которых подписан текущий пользователь
        following_users = User.objects.filter(followers__follower=request.user)
        
        # Получаем посты от этих пользователей
        posts = Post.objects.filter(author__in=following_users).order_by('-created_at')
        
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

class NotificationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    def patch(self, request):
        # Отметить все уведомления как прочитанные
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'All notifications marked as read.'}, status=status.HTTP_200_OK)

class SearchView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response({'detail': 'Search query is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Поиск пользователей
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )[:10]
        
        # Поиск постов
        posts = Post.objects.filter(content__icontains=query).order_by('-created_at')[:20]
        
        users_serializer = UserSerializer(users, many=True, context={'request': request})
        posts_serializer = PostSerializer(posts, many=True, context={'request': request})
        
        return Response({
            'users': users_serializer.data,
            'posts': posts_serializer.data
        })