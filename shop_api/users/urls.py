# urls.py
from django.urls import path
from .views import RegisterView, ConfirmUserView, LoginView

urlpatterns = [
    path('api/v1/users/register/', RegisterView.as_view(), name='register'),
    path('api/v1/users/confirm/', ConfirmUserView.as_view(), name='confirm'),
    path('api/v1/users/login/', LoginView.as_view(), name='login'),
]