from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from polls.views import PollHistoryView
from .views import (
    SignUpView,
    SingInView,
    LogoutView,
    StartPointView,
    UserCabinView,
    TeacherView, SendEmailView,
)

extra_patterns = [
    path(
        "",
        PollHistoryView.as_view(),
        name="HistoryView",
    ),
    path(
        "<str:poll_title>/<int:user_id>",
        PollHistoryView.as_view(),
        name="HistoryDetailView",
    ),
]

urlpatterns = [
    path("sign_up/", SignUpView.as_view(), name="SignUpView"),
    path("sign_in/", SingInView.as_view(), name="SignIpView"),
    path("logout/", LogoutView.as_view(), name="LogoutView"),
    path("cabin/", UserCabinView.as_view(), name="UserCabinView"),
    path("", StartPointView.as_view(), name="HomeView"),
    path("cabin/history/", include(extra_patterns)),
    path("teacher", TeacherView.as_view(), name="TeacherView"),
    path("cabin/send_email/", SendEmailView.as_view(), name="SendEmailView")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
