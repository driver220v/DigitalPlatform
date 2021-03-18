from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from platformUsers.forms import ProfileForm, UserForm
from platformUsers.models import Profile


# coverage run --source='.' manage.py test platformUsers.tests.test_urls
from polls.models import Poll


class UrlTestCases(TestCase):
    def setUp(self) -> None:
        self.login_data = {"username": "TestUser123", "password": "TestUserPassword123"}

        data_user = {
            "username": "TestUser123",
            "first_name": "TestUserFirstName",
            "last_name": "TestUserLastName",
            "email": "TestUser@email.com",
        }
        data_profile = {"ph_number": "89673876987", "user_type": "teacher"}

        User.objects.create(**data_user)

        user = User.objects.get(username="TestUser123")

        user.set_password("TestUserPassword123")
        user.save()
        Profile.objects.filter(user=user).update(**data_profile)
        self.client = Client()

    def test_signup_user(self):
        user_form = UserForm(
            data={
                "username": "TestUserNew",
                "first_name": "TestUserNewFirstName",
                "last_name": "TestUserNewLastName",
                "email": "TestNewUser@email.com",
                "password1": "Test_not_so_similar_password_New123",
                "password2": "Test_not_so_similar_password_New123",
            }
        )
        profile_form = ProfileForm(
            data={"ph_number": "89673876980", "user_type": "teacher"}
        )
        # self.assertTrue(user_form.is_valid())
        if not user_form.is_valid():
            print(user_form.errors)
        self.assertTrue(profile_form.is_valid())

    def test_get_users_url(self):
        home_view = self.client.get(reverse("HomeView"))
        self.assertEqual(home_view.status_code, 200)

    def test_login_user(self):
        existing_user = self.client.login(
            **{"username": "TestUser123", "password": "TestUserPassword123"}
        )
        non_existing_user = self.client.login(
            **{
                "username": "TestUser_not_exist",
                "password": "TestUserPassword_not_exist",
            }
        )
        self.assertTrue(existing_user)
        self.assertFalse(non_existing_user)

    def test_login_user_redirects(self):
        sign_in = reverse("SignIpView")
        response = self.client.post(
            sign_in,
            data={"username": "TestUser123", "password": "TestUserPassword123"},
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("HomeView"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_has_teacher_cabin(self):
        self.client.login(**self.login_data)
        response = self.client.get(reverse("HomeView"))
        self.assertContains(
            response,
            f'<a href="{reverse("TeacherView")}"> TeacherHeadquarters </a>',
            html=True,
        )
        response_teacher = self.client.get(reverse("TeacherView"))
        self.assertEqual(response_teacher.status_code, 200)
        poll_tup = [
            (f"{poll_title}", f"{poll_title}")
            for poll_title in Poll.objects.values_list("poll_title", flat=True)
        ]
        users_tup = [
            (f"{username}", f"{username}")
            for username in User.objects.values_list("username", flat=True)
        ]
        self.assertEquals(response_teacher.context["form"].poll_tup, poll_tup)
        self.assertEqual(response_teacher.context["form"].poll_tup, users_tup)
