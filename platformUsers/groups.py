from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group


def __add_user_to_gr(user: User, gr_name: str):
    my_group = Group.objects.get(name=gr_name)
    my_group.user_set.add(user)


def add_permission(user: User, gr_name: str):
    teachers_group, created = Group.objects.get_or_create(name=gr_name)
    if created:

        ct = ContentType.objects.get_for_model(User)
        permission = Permission.objects.create(
            codename="Gr_codename", name="Digital platform group", content_type=ct
        )
        teachers_group.permissions.add(permission)
    __add_user_to_gr(user, gr_name)
