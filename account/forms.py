from .models import User, Post, User_Ip
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.files.images import get_image_dimensions


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']


class UserIpForm(forms.ModelForm):
    class Meta:
        model = User_Ip
        fields = ['user','ip_address']


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']

        try:
            w, h = get_image_dimensions(avatar)

            #validate dimensions
            max_width = max_height = 100
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                     '%s x %s pixels or smaller.' % (max_width, max_height))

            #validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                    'GIF or PNG image.')

            #validate file size
            if len(avatar) > (30 * 1024):
                raise forms.ValidationError(
                    u'Avatar file size may not exceed 30k.')

        except AttributeError:
            """
            Handles case when we are updating the user profile
			and do not supply a new avatar
            """
            pass

        return avatar