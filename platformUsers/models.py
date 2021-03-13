from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ph_number = models.IntegerField(null=True)
    avatar = models.ImageField(upload_to="profile_pictures", null=True)
    user_type = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.user}"s profile'
