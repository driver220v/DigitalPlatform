from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.transaction import atomic
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.encoding import iri_to_uri
from django.views.generic import View, UpdateView
from polls.models import Poll
from polls.permissions import TeacherPermission
from .forms import ProfileForm, UserForm, AuthForm, UpdateProfileForm, UserSelectForm, SendEmailForm
from .groups import add_permission
from .models import Profile
from .pass_test import is_teacher
from .emailer import send_email


# Create your views here.


class SignUpView(View):
    user_form = UserForm
    profile_form = ProfileForm

    def get(self, request):
        return render(
            request,
            "platformUsers/index.html",
            context={"profile": self.profile_form, "user": self.user_form()},
        )

    @atomic
    def post(self, request):
        user_form = self.user_form(data=request.POST)
        profile_form = self.profile_form(data=request.POST)
        if profile_form.is_valid() and user_form.is_valid():
            user = user_form.save(profile_data=profile_form.cleaned_data)
            if profile_form.cleaned_data["user_type"] == "teacher":
                add_permission(user, "teachers")
            login(request, user)
            return HttpResponseRedirect(reverse("HomeView"))
        return render(
            request,
            "platformUsers/index.html",
            context={"profile": profile_form, "user": user_form},
        )


class StartPointView(View):
    def get(self, request):
        return render(request, "platformUsers/start.html")


class LogoutView(View):
    def get(self, request):
        if not request.user.is_anonymous:
            logout(request)
        response = reverse("HomeView")

        return HttpResponseRedirect(response)


class SingInView(View):
    auth_form = AuthForm

    def get(self, request):
        if not request.user.is_authenticated:
            return render(
                request, "platformUsers/index.html", context={"user": self.auth_form()}
            )
        return HttpResponseRedirect(reverse("HomeView"))

    def post(self, request):
        form = self.auth_form(data=request.POST)
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("HomeView"))
        return render(request, "platformUsers/index.html", context={"user": form})


class UserCabinView(LoginRequiredMixin, UpdateView, View):
    login_url = "/sign_in/"
    model = Profile
    template_name = "platformUsers/user_cabin.html"
    form_class = UpdateProfileForm
    success_url = "/"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.user.profile.pk)


class TeacherView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "/sign_in/"
    form = UserSelectForm

    def test_func(self):
        # todo implement way to 403
        is_true = is_teacher(self.request.user)
        if is_true:
            return is_true
        return HttpResponseForbidden()

    def get(self, request, *args, **kwargs):
        form = self.form()
        return render(request, "platformUsers/teacher.html", context={"form": form})

    def post(self, request, *args, **kwargs):
        input_data = self.form(data=request.POST)
        if input_data.is_valid():
            user = User.objects.get(username=input_data.cleaned_data["select_username"])
            """Filter that a selected user has passed selected test"""
            has_answered_poll = Poll.objects.filter(
                Q(questions__answer__user=user.id)
                & Q(poll_title=input_data.cleaned_data["select_poll_t"])
            ).exists()
            if has_answered_poll:
                response = reverse(
                    "HistoryDetailView",
                    args=[
                        iri_to_uri(input_data.cleaned_data["select_poll_t"]),
                        user.id,
                    ],
                )

                return HttpResponseRedirect(response)
            raise Http404


class SendEmailView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "/sign_in/"
    form = SendEmailForm

    def test_func(self):
        # todo implement way to 403
        is_true = is_teacher(self.request.user)
        if is_true:
            return is_true
        return HttpResponseForbidden()

    def get(self, request, *args, **kwargs):
        return render(request, 'platformUsers/send_email.html', context={"email": self.form()})

    @atomic
    def post(self, request, *args, **kwargs):
        data = self.form(data=request.POST)
        if data.is_valid():
            body = data.cleaned_data["user_question"]
            teach_email = User.objects.filter(username=data.cleaned_data["teacher_username"]).values_list("email",
                                                                                                          flat=True)
            send_email(body, request.user, list(teach_email))
