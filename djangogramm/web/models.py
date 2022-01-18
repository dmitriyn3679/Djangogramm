from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField()
    avatar = models.ImageField(upload_to=f'{settings.MEDIA_FOLDER}/avatars', blank=True, null=True)

    follows = models.ManyToManyField('self', db_table='web_follows', related_name='followed_by', symmetrical=False)
    followers = models.ManyToManyField('self', db_table='web_followers', related_name='follow_to', symmetrical=False)

    @property
    def full_name(self):
        return self.get_full_name()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    likes = models.ManyToManyField(User, db_table='web_post_like_user', related_name='posts_likes')


class Media(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    media = models.ImageField(upload_to=f'{settings.MEDIA_FOLDER}/media')


class Comment(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    likes = models.ManyToManyField(User, db_table='web_comment_likes_user', related_name='comments_likes')


class Dialog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Message(models.Model):
    text = models.TextField()
    sender = models.ForeignKey(User, related_name='sent_message', on_delete=models.SET_NULL, null=True)
    recipient = models.ForeignKey(User, related_name='input_message', on_delete=models.SET_NULL, null=True)
    dialog = models.ForeignKey(Dialog, on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
