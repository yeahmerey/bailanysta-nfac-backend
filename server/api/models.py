from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models.signals import post_save


class Post(models.Model): 
    author = models.ForeignKey(User, on_delete=models.CASCADE , related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)


    def like_count(self):
        return self.likes.count()
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} on {self.post.id}'