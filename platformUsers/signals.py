from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from platformUsers.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        prof_args = getattr(instance, '_prof_data', None)
        Profile.objects.create(user=instance, **prof_args)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
