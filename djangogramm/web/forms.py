from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm


from web.models import User, Post, Media, Comment


class BaseFormMixin:
    def __init__(self, *args, **kwargs):
        super(BaseFormMixin, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class UserLoginForm(BaseFormMixin, AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'placehodler': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placehodler': 'Password'}))


class SignUpForm(BaseFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=123, help_text='Required')
    bio = forms.CharField(widget=forms.Textarea(), max_length=1024, required=False, help_text='Optional')
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'bio', 'avatar')


class PostForm(BaseFormMixin, forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))

    class Meta:
        model = Post
        fields = ('text',)


class MediaForm(BaseFormMixin, forms.ModelForm):
    media = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Media
        fields = ('media',)


class CommentForm(BaseFormMixin, forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label='Write Comment')

    class Meta:
        model = Comment
        fields = ('text',)



