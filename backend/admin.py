# admin.py
from django.contrib import admin
from .models import (
    Event,
    Review,
    UserEvent,
    Chat,
    Profile,
    SuspendedUser,
    BannedUser,
    ChatRoom3,
    Room3,
    user_rooms,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

admin.site.register(Event)
admin.site.register(Review)
admin.site.register(UserEvent)
admin.site.register(Chat)
admin.site.register(Profile)
admin.site.register(ChatRoom3)
admin.site.register(Room3)
admin.site.register(user_rooms)


class SuspendedUserInline(admin.StackedInline):
    model = SuspendedUser
    can_delete = False
    verbose_name_plural = "Suspended Users"
    readonly_fields = ["suspended_at"]


class BannedUserInline(admin.StackedInline):
    model = BannedUser
    can_delete = False
    verbose_name_plural = "Banned Users"
    readonly_fields = ["banned_at"]


def send_notification_email(user, subject, message):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)


class UserAdmin(BaseUserAdmin):
    inlines = (
        SuspendedUserInline,
        BannedUserInline,
    )
    actions = ["ban_user", "unban_user", "suspend_user", "unsuspend_user"]

    def ban_user(self, request, queryset):
        for user in queryset:
            banned_user, created = BannedUser.objects.get_or_create(
                user=user, defaults={"reason": "Reason for ban goes here"}
            )
            if created:
                user.is_active = False
                user.save()
                # Send an email notification
                subject = "Your Account Has Been Banned"
                message = "Your account has been banned. If you believe this is a mistake, please contact support."
                send_notification_email(user, subject, message)
                self.message_user(
                    request, f"User {user.username} has been banned successfully."
                )
            else:
                self.message_user(
                    request,
                    f"User {user.username} is already banned.",
                    level=messages.WARNING,
                )

    ban_user.short_description = "Ban selected users"

    def unban_user(self, request, queryset):
        for user in queryset:
            banned_user = BannedUser.objects.filter(user=user).first()
            if banned_user:
                banned_user.delete()
                user.is_active = True
                user.save()
                self.message_user(
                    request, f"User {user.username} has been unbanned successfully."
                )
            else:
                self.message_user(
                    request,
                    f"User {user.username} is not currently banned.",
                    level=messages.WARNING,
                )

    unban_user.short_description = "Unban selected users"

    def suspend_user(self, request, queryset):
        for user in queryset:
            suspended_user, created = SuspendedUser.objects.get_or_create(
                user=user,
                defaults={
                    "reason": "Reason for suspension goes here",
                    "is_suspended": True,
                },
            )
            if created:
                # Send an email notification
                subject = "Your Account Has Been Suspended"
                message = "Your account has been suspended. If you believe this is a mistake, please contact support."
                send_notification_email(user, subject, message)
                self.message_user(
                    request, f"User {user.username} has been suspended successfully."
                )
            else:
                self.message_user(
                    request,
                    f"User {user.username} is already suspended.",
                    level=messages.WARNING,
                )

    suspend_user.short_description = "Suspend selected users"

    def unsuspend_user(self, request, queryset):
        for user in queryset:
            try:
                suspended_user = SuspendedUser.objects.get(user=user)
                suspended_user.unsuspend_user()
                self.message_user(
                    request, f"User {user.username} has been unsuspended successfully."
                )
            except SuspendedUser.DoesNotExist:
                self.message_user(
                    request,
                    f"User {user.username} is not suspended.",
                    level=messages.WARNING,
                )

    unsuspend_user.short_description = "Unsuspend selected users"

    def is_banned(self, obj):
        return hasattr(obj, "banneduser")

    is_banned.boolean = True
    is_banned.admin_order_field = "banneduser"

    def is_suspended(self, obj):
        return hasattr(obj, "suspendeduser") and obj.suspendeduser.is_suspended

    is_suspended.boolean = True
    is_suspended.admin_order_field = "suspendeduser__is_suspended"

    list_display = BaseUserAdmin.list_display + (
        "is_banned",
        "is_suspended",
    )
    list_filter = BaseUserAdmin.list_filter + (
        "banneduser",
        "suspendeduser__is_suspended",
    )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class SuspendedUserAdmin(admin.ModelAdmin):
    list_display = [
        "get_username",
        "get_email",
        "reason",
        "suspended_at",
        "unsuspended_at",
        "is_suspended",
    ]
    list_filter = ["suspended_at", "unsuspended_at", "is_suspended"]

    def get_username(self, obj):
        return obj.user.username

    get_username.admin_order_field = "user__username"

    def get_email(self, obj):
        return obj.user.email

    get_email.admin_order_field = "user__email"
    get_email.short_description = "Email"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_active=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BanneddUserAdmin(admin.ModelAdmin):
    list_display = [
        "get_username",
        "get_email",
        "reason",
        "banned_at",
        "unban_at",
    ]
    list_filter = ["banned_at", "unban_at"]

    def get_username(self, obj):
        return obj.user.username

    get_username.admin_order_field = "user__username"

    def get_email(self, obj):
        return obj.user.email

    get_email.admin_order_field = "user__email"
    get_email.short_description = "Email"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_active=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(BannedUser, BanneddUserAdmin)
admin.site.register(SuspendedUser, SuspendedUserAdmin)
