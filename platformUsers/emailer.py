from django.contrib.auth.models import User
from django.core.mail import EmailMessage


def send_email(body, user: User, receive_email: list):

    email = EmailMessage("Question", body, f"driver220w@yandex.ru", receive_email)
    email.send(fail_silently=False)
