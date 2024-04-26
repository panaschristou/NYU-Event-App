from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Profile
from django.conf import settings
from .models import SuspendedUser, BannedUser
from django.utils import timezone


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
    else:
        subject = "Your account has been unsuspended"
        message = f"Dear {instance.user.username},\n\nYour account has been unsuspended \n\nSincerely,\nThe Admin Team"
        sender_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = instance.user.email
        send_mail(subject, message, sender_email, [recipient_email])


@receiver(post_save, sender=BannedUser)
def send_ban_notification(sender, instance, **kwargs):
    if not instance.user.is_active:
        subject = "Your account has been banned"
        message = f"Dear {instance.user.username},\n\nYour account has been banned due to the following reason:\n\n{instance.reason}\n\nIf you believe this is an error, please contact support.\n\nSincerely,\nThe Admin Team"
        sender_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = instance.user.email
        send_mail(subject, message, sender_email, [recipient_email])

    else:
        subject = "Your account has been unbanned"
        message = f"Dear {instance.user.username},\n\nYour account has been unbanned \n\nSincerely,\nThe Admin Team"
        sender_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = instance.user.email
        send_mail(subject, message, sender_email, [recipient_email])


@receiver(post_delete, sender=BannedUser)
def send_notification_email(sender, instance, **kwargs):
    user = instance.user
    user.is_active = True
    user.save()
    email_subject = "Account Notification"
    email_body = f"Dear {instance.user.username},\n\nYour account has been unbanned \n\nSincerely,\nThe Admin Team"
    send_mail(email_subject, email_body, "from@example.com", [user.email])


@receiver(post_delete, sender=SuspendedUser)
def send_notification(sender, instance, **kwargs):
    user = instance.user
    email_subject = "Account Notification"
    email_body = f"Dear {instance.user.username},\n\nYour account has been unsuspended \n\nSincerely,\nThe Admin Team"
    send_mail(email_subject, email_body, "from@example.com", [user.email])
