from django.db.models.signals import post_save
from django.dispatch import receiver
from online_shop.models import UserAccount

@receiver(post_save, sender=UserAccount)
def send_welcomde_email(sender, instance, created, **kwargs):
    if created:
        print('Welcome', instance.email)