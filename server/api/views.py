from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status , permissions 
from django.contrib.auth.models import User
from api.serializers import CommentSerializer, PostSerializer, RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Comment, Post
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