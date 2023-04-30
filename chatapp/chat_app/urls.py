from django.urls import path
from .views import RegisterView, LoginView, MessageList, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('messages/', MessageList.as_view(), name='messages-list'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
