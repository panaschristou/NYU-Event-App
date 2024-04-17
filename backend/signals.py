from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Profile
from django.conf import settings
from .models import SuspendedUser


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=SuspendedUser)
def send_suspension_notification(sender, instance, **kwargs):
    if instance.is_suspended:
        subject = "Your account has been suspended"
        message = f"Dear {instance.user.username},\n\nYour account has been suspended due to the following reason:\n\n{instance.reason}\n\nIf you believe this is an error, please contact support.\n\nSincerely,\nThe Admin Team"
        sender_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = instance.user.email
        send_mail(subject, message, sender_email, [recipient_email])
