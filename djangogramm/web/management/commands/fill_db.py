import random
import sys
import shutil

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from factory.django import DjangoModelFactory, ImageField as IF
from factory import Faker, LazyAttribute
from django.db import transaction
import requests
from io import BytesIO
from uuid import uuid4
from functools import wraps

from web.models import User, Post, Comment, Message, Media


CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
END = '\033[0m'


def status(func):
    @wraps(func)
    def inner(*args, **kwargs):
        func_name = func.__name__.replace('_', ' ').upper().ljust(50, '.')
        print(f'{func_name} {BOLD}{RED}RUNNING{END}')
        res = func(*args, **kwargs)
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)
        print(f'{func_name} {BOLD}{GREEN}DONE{END}')
        return res
    return inner


class ImageField(IF):
    def _make_data(self, params):
        width = params.get('width', 100)
        url = f'https://picsum.photos/{width}'
        resp = requests.get(url)
        return BytesIO(resp.content).getvalue()


def get_image(size=128):
    def inner(_):
        return ContentFile(ImageField()._make_data({'width': size}), f'{uuid4().hex}.jpg')
    return inner


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    username = Faker('word')
    email = Faker('email')
    bio = Faker('text')
    avatar = LazyAttribute(get_image())
    first_name = Faker('first_name')
    last_name = Faker('last_name')


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post
    text = Faker('paragraph')


class MediaFactory(DjangoModelFactory):
    class Meta:
        model = Media
    media = LazyAttribute(get_image(1024))


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment
    text = Faker('sentence')


class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message
    text = Faker('sentence')


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    USER_COUNT = 10

    POST_MIN_COUNT = 1
    POST_MAX_COUNT = 5

    MIN_LIKES_PER_POST = 1
    MAX_LIKES_PER_POST = USER_COUNT - 1

    MIN_COMMENTS_PER_POST = 5
    MAX_COMMENTS_PER_POST = USER_COUNT - 1

    MIN_LIKES_PER_COMMENT = 0
    MAX_LIKES_PER_COMMENT = 7

    MIN_FOLLOWERS_COUNT = 1
    MAX_FOLLOWERS_COUNT = USER_COUNT - 1

    MIN_MEDIA_PER_POST = 2
    MAX_MEDIA_PER_POST = 5

    models = (User, Post, Comment, Message, Media)

    @status
    def clear_models(self):
        try:
            shutil.rmtree(settings.MEDIA_FOLDER)
        except FileNotFoundError as e:
            pass
        for model in self.models:
            model.objects.all().delete()

    @status
    def generate_users(self):
        users = []
        for _ in range(self.USER_COUNT):
            user = UserFactory()
            user.set_password('12321qqq123')
            user.save()
            users.append(user)
        return users

    @status
    def generate_posts_and_likes(self, users):
        posts = []
        for user in users:
            for _ in range(random.randint(self.POST_MIN_COUNT, self.POST_MAX_COUNT)):
                post = PostFactory(user=user)
                for _ in range(random.randint(self.MIN_MEDIA_PER_POST, self.MAX_MEDIA_PER_POST)):
                    MediaFactory(post=post)
                post.likes.set(random.sample(users, random.randint(self.MIN_LIKES_PER_POST, self.MAX_LIKES_PER_POST)))
                posts.append(post)
        return posts

    @status
    def generate_comments_and_likes(self, posts, users):
        for post in posts:
            for _ in range(random.randint(self.MIN_COMMENTS_PER_POST, self.MAX_COMMENTS_PER_POST)):
                comment = CommentFactory(post=post, user=random.choice(users))
                comment.likes.set(
                    random.sample(users, random.randint(self.MIN_LIKES_PER_COMMENT, self.MAX_LIKES_PER_POST)))

    @status
    def generate_followers_and_follows(self, users):
        for user in users:
            followers = {follower
                         for follower in
                         random.sample(users, random.randint(self.MIN_FOLLOWERS_COUNT, self.MAX_FOLLOWERS_COUNT))
                         if follower != user}
            follows = {follow
                       for follow in
                       random.sample(users, random.randint(self.MIN_FOLLOWERS_COUNT, self.MAX_FOLLOWERS_COUNT))
                       if follow != user}
            user.followers.set(followers)
            user.follows.set(follows)

    @transaction.atomic
    def handle(self, *args, **options):
        self.clear_models()

        users = self.generate_users()
        self.generate_followers_and_follows(users)
        posts = self.generate_posts_and_likes(users)
        self.generate_comments_and_likes(posts, users)

        print('Data created')
