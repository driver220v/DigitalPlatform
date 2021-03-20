from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from platformUsers.forms import ProfileForm, UserForm
from platformUsers.groups import add_permission
from platformUsers.models import Profile
from platformUsers.tests import info_tests
# coverage run --source='.' manage.py test platformUsers.tests.test_urls
from polls.models import Poll, PollQuestion, PollQuestionChoices


class UrlTestCases(TestCase):
    def tearDown(self) -> None:
        Poll.objects.all().delete()

    def setUp(self) -> None:
        """create user-teacher objects"""
        info_data_user = info_tests.get_user_info()["teacher"]
        User.objects.create(**info_data_user["user_d"])
        self.user_teacher = User.objects.get(username="TestUser123")

        self.login_data_teacher = {"username": "TestUser123",
                                   "password": "TestUserPassword123"}

        add_permission(self.user_teacher, "teachers")
        self.user_teacher.set_password("TestUserPassword123")
        self.user_teacher.save()
        Profile.objects.filter(user=self.user_teacher).update(**info_data_user["profile"])
        """Create user-student object"""
        info_data_user = info_tests.get_user_info()['student']
        User.objects.create(**info_data_user["user_d"])

        self.user_student = User.objects.get(username="TestUser123Student_student")
        self.login_data_student = {"username": "TestUser123Student_student",
                                   "password": "TestUser123Student_student"}
        self.user_student.set_password("TestUser123Student_student")
        self.user_student.save()
        Profile.objects.filter(user=self.user_student).update(**info_data_user["profile"])
        """Create polls objects"""
        self.polls_data = info_tests.get_polls()
        for data_p in self.polls_data:
            poll_q = data_p.pop("questions")
            poll = Poll.objects.create(**data_p)
            for question in poll_q:
                choices = question.pop("choices")
                question = PollQuestion.objects.create(**question, poll=poll)
                PollQuestionChoices.objects.bulk_create([PollQuestionChoices(question=question, **choice_data)
                                                         for choice_data in choices])
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
            data={"ph_number": "89673876989", "user_type": "teacher"}
        )
        self.assertTrue(user_form.is_valid())
        self.assertTrue(profile_form.is_valid())

    def test_get_users_url(self):
        home_view = self.client.get(reverse("HomeView"))
        self.assertEqual(home_view.status_code, 200)

    def test_login_user(self):
        existing_user = self.client.login(
            **self.login_data_teacher
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
        sign_in = reverse("SignInView")
        response = self.client.post(
            sign_in,
            data={"username": "TestUser123",
                  "password": "TestUserPassword123"},
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
        self.client.login(**self.login_data_teacher)
        response = self.client.get(reverse("HomeView"))
        self.assertContains(
            response,
            f'<a href="{reverse("TeacherView")}"> TeacherHeadquarters </a>',
            html=True,
        )
        response_teacher = self.client.get(reverse("TeacherView"))
        self.assertEqual(response_teacher.status_code, 200)

    def test_get_polls(self):
        self.client.login(**self.login_data_teacher)
        response = self.client.get(reverse("PollsView"))
        self.assertEqual(response.status_code, 200)
        for idx, _ in enumerate(range(len(self.polls_data) + 10), 1):
            url = reverse("PollDetailView", args=[idx])
            response = self.client.get(url)
            if idx <= len(self.polls_data):
                self.assertEqual(response.status_code, 200)
            else:
                self.assertEqual(response.status_code, 404)

    def test_pass_poll(self):
        url = reverse("PollDetailView", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.login(**self.login_data_teacher)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res = self.client.post(url, data={"answers": {"8": 1, "2": 28}}, content_type='application/json')
        self.assertContains(res, 'Question ID is not applicable for this Poll', status_code=400)

        res = self.client.post(url, data={"answers": {"1": 1, "2": 2}}, content_type='application/json')
        self.assertContains(res, 'Invalid choice ID. Choice ID is not applicable for this Question ID', status_code=400)

    def test_null_result(self):
        self.client.login(**self.login_data_student)
        url = reverse("PollDetailView", args=[1])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        """student has answered poll where id=1"""
        res = self.client.post(url, data={"answers": {"1": 2, "2": 5}}, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        """attempt to asnwer poll second time"""
        res = self.client.post(url, data={"answers": {"1": 4, "2": 6}}, content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertContains(res, 'already answered', status_code=400)
        self.client.logout()
        self.client.login(**self.login_data_teacher)
        resp = self.client.get(reverse('TeacherView'))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(reverse('TeacherView'), data={"select_username": self.login_data_student["username"],
                                                              'select_poll_t': "Природные ископаемые"})

        self.assertEqual(resp.status_code, 302)
        resp_del = self.client.delete(reverse('HistoryDetailView', args=[self.login_data_student["username"],
                                                                         self.user_student.id]))
        self.assertEqual(resp_del.status_code, 202)
