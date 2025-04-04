from django.contrib.auth import get_user_model

from online_shop.models import UserAccount


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    User = get_user_model()
    if user:
        return {'is_new': False}

    fields = {

        'email': details['email'],
        'is_active': True,
        'is_staff': True,
        'is_superuser': True
    }
    user, created = User.objects.get_or_create(**fields)
    return {
        'is_new': created,
        'user': user
    }
