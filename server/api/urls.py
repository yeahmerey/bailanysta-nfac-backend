from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from api.views import (
    LikePostView,
    PostListCreateView,
    PostRetrieveUpdateDestroyView,
    RegisterView , 
    LogoutView,
    UnlikePostView , 
)


urlpatterns = [
    path('register/' , RegisterView.as_view() , name='register'),
    path('login/' , TokenObtainPairView.as_view() , name='login'),
    path('logout/' , LogoutView.as_view() , name='logout'),
    path('token/refresh/' , TokenRefreshView.as_view() , name='token_refresh'),

    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', LikePostView.as_view(), name='post-like'),
    path('posts/<int:pk>/unlike/', UnlikePostView.as_view(), name='post-unlike'),
]
