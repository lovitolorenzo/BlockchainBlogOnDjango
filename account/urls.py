from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('register/', views.registerPage, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
	path('user_data/<int:pk>', views.user_data, name='user_data'),
	path('user_posts/<int:pk>', views.user_posts, name='user_posts'),
    path('postcounter', views.postcounter, name='postcounter'),
    path('json/last_hour', views.last_hour_posts, name='last_hour_posts'),
	path('transaction/verification', views.transaction_verification, name='transaction_verification'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
