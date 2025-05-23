from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from api.views import (
    CommentDetailView,
    FeedView,
    FollowUserView,
    LikePostView,
    NotificationsView,
    PostCommentsView,
    PostListCreateView,
    PostRetrieveUpdateDestroyView,
    ProfileView,
    RegisterView , 
    LogoutView,
    SearchView,
    UnfollowUserView,
    UnlikePostView,
    UserFollowersView,
    UserFollowingView,
    UserPostsView,
    UserProfileView,
)
from server import settings
from django.conf.urls.static import static


urlpatterns = [
    path('register/' , RegisterView.as_view() , name='register'),
    path('login/' , TokenObtainPairView.as_view() , name='login'),
    path('logout/' , LogoutView.as_view() , name='logout'),
    path('token/refresh/' , TokenRefreshView.as_view() , name='token_refresh'),

    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', LikePostView.as_view(), name='post-like'),
    path('posts/<int:pk>/unlike/', UnlikePostView.as_view(), name='post-unlike'),


    path('posts/<int:post_id>/comments/', PostCommentsView.as_view(), name='post-comments'),
    path('posts/<int:post_id>/comments/<int:comment_id>/', CommentDetailView.as_view(), name='comment-detail'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('users/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('users/<str:username>/posts/', UserPostsView.as_view(), name='user-posts'),
    
    # Подписки
    path('users/<str:username>/follow/', FollowUserView.as_view(), name='follow-user'),
    path('users/<str:username>/unfollow/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('users/<str:username>/followers/', UserFollowersView.as_view(), name='user-followers'),
    path('users/<str:username>/following/', UserFollowingView.as_view(), name='user-following'),
    
    # Лента и уведомления
    path('feed/', FeedView.as_view(), name='feed'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    
    # Поиск
    path('search/', SearchView.as_view(), name='search'),

]