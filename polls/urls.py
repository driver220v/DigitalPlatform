from django.contrib import admin
from django.urls import path, include
from .views import PollsView

urlpatterns = [
    path('', PollsView.as_view())
]