from django.urls import path
from.views import sign_up, profile, invite
urlpatterns = [
    path('sign_up/', sign_up),
    path('profile/<int:id>/', profile),
    path('profile/<int:id>/', profile),
    path('sign_up/<str:coupon>', invite),
    ]