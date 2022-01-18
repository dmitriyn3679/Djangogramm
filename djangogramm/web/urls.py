from web import views, forms
from django.contrib.auth.views import LoginView, LogoutView

from django.urls import include, path
from web import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'post', views.GroupViewSet)


app_name = 'web'
urlpatterns = [
    path('', views.feed, name='feed'),
    path('profile/<slug:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post, name='post'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/comments/', views.comment_create, name='comment_create'),

    path('api/', include(router.urls)),

    path(
        'login/',
        LoginView.as_view(
            template_name="login.html",
            authentication_form=forms.UserLoginForm
        ),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),

    path('ajax/like_post', views.like_handler, name='like_handler'),


    # path('create_post', views.create_post, name='create_post'),
]