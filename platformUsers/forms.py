from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

from .enums import PlatformUserEnum
from .models import Profile


class ProfileForm(forms.ModelForm):
    user_type = forms.ChoiceField(required=True, choices=PlatformUserEnum.choices())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.non_required:
            self.fields[field].required = False

    class Meta:
        model = Profile
        fields = "__all__"
        exclude = [
            "user",
        ]
        non_required = ["ph_number", "avatar"]


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def save(self, commit=True, *args, **kwargs):
        user = super().save(commit=False)
        prof_data = kwargs.get("profile_data", None)
        user._prof_data = prof_data
        if commit:
            user.save()

        return user


class AuthForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data["username"]
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Username {username} is already in use.")
        return username

    class Meta:
        model = User


class UpdateProfileForm(forms.ModelForm):
    user_type = forms.ChoiceField(required=True, choices=PlatformUserEnum.choices())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.non_required:
            self.fields[field].required = False

    class Meta:
        model = Profile
        fields = "__all__"
        exclude = ("user",)
        non_required = ["ph_number", "avatar"]

    def clean_user_type(self):
        if self.instance:
            return self.instance.user_type

        else:
            return self.fields["user_type"]
