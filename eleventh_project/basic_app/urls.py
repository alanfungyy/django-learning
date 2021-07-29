from django.urls import path
from .views import index, form, user_logout, special, user_login

app_name = 'basic_app'

urlpatterns = [
    path('', index, name='index'),
    path('form/', form, name='form'),
    path('logout/', user_logout, name='logout'),
    path('special/', special, name='special'),
    path('login/', user_login, name='login'),
]
