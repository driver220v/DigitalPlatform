from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View, UpdateView
from .forms import ProfileForm, UserForm, AuthForm, UpdateProfileForm
from .models import Profile


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
        return HttpResponseRedirect(reverse("HomeView"))


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


class UserCabinView(LoginRequiredMixin, UpdateView):
    login_url = "/sign_in/"
    model = Profile
    template_name = "platformUsers/user_cabin.html"
    form_class = UpdateProfileForm
    success_url = "/"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.user.profile.pk)
