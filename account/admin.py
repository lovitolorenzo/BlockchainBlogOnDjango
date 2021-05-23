from django.contrib import admin

# Register your models here.

from .models import Post
from .models import User_Ip
from .models import User

admin.site.register(Post)
admin.site.register(User_Ip)
admin.site.register(User)