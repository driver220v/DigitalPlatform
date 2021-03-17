from django.contrib import admin
from django.urls import path, include
from .views import PollsView, PollDetailView, PollHistoryView

urlpatterns = [
    path("", PollsView.as_view(), name="PollsView"),
    path("<int:pk>", PollDetailView.as_view()),
]
