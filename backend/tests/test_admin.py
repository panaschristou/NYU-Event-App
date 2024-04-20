from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from backend.admin import (
    UserAdmin,
    SuspendedUserInline,
    BannedUserInline,
    SuspendedUserAdmin,
    BanneddUserAdmin,
)
from backend.models import SuspendedUser, BannedUser
from django.contrib import admin
from unittest.mock import Mock


class TestUserAdmin(TestCase):
    def setUp(self):
        self.admin_site = admin.AdminSite()
        self.user_admin = UserAdmin(User, self.admin_site)

    def test_inlines(self):
        self.assertIn(SuspendedUserInline, self.user_admin.inlines)
        self.assertIn(BannedUserInline, self.user_admin.inlines)

    def test_actions(self):
        expected_actions = ["ban_user", "unban_user", "suspend_user", "unsuspend_user"]
        self.assertEqual(self.user_admin.actions, expected_actions)

    def test_ban_user(self):
        request = Mock()
        request.user = Mock()
        user = User.objects.create(username="test_user")
        self.user_admin.ban_user(request, User.objects.filter(pk=user.pk))
        banned_user = BannedUser.objects.filter(user=user).first()
        self.assertIsNotNone(banned_user)
        self.assertFalse(banned_user.user.is_active)

    def test_unban_user(self):
        request = Mock()
        request.user = Mock()
        user = User.objects.create(username="test_user")
        self.user_admin.ban_user(request, User.objects.filter(pk=user.pk))
        banned_user = BannedUser.objects.filter(user=user).first()
        self.assertIsNotNone(banned_user)
        self.assertFalse(banned_user.user.is_active)
        self.user_admin.unban_user(request, User.objects.filter(pk=user.pk))
        banned_user = BannedUser.objects.filter(user=user).first()
        self.assertIsNone(banned_user)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_suspend_user(self):
        request = Mock()
        request.user = Mock()
        user = User.objects.create(username="test_user")
        self.user_admin.suspend_user(request, User.objects.filter(pk=user.pk))
        suspended_user = SuspendedUser.objects.filter(user=user).first()
        self.assertIsNotNone(suspended_user)
        self.assertTrue(suspended_user.is_suspended)

    def test_unsuspend_user(self):
        request = Mock()
        request.user = Mock()
        user = User.objects.create(username="test_user")
        self.user_admin.suspend_user(request, User.objects.filter(pk=user.pk))
        suspended_user = SuspendedUser.objects.filter(user=user).first()
        self.assertIsNotNone(suspended_user)
        self.assertTrue(suspended_user.is_suspended)
        self.user_admin.unsuspend_user(request, User.objects.filter(pk=user.pk))
        suspended_user = SuspendedUser.objects.filter(user=user).first()
        self.assertIsNone(suspended_user)
        user.refresh_from_db()

    def test_is_banned(self):
        user = User.objects.create(username="test_user")
        self.assertFalse(self.user_admin.is_banned(user))
        banned_user = BannedUser.objects.create(user=user)
        self.assertTrue(self.user_admin.is_banned(banned_user.user))

    def test_is_suspended(self):
        user = User.objects.create(username="test_user")
        self.assertFalse(self.user_admin.is_suspended(user))
        suspended_user = SuspendedUser.objects.create(user=user, is_suspended=True)
        self.assertTrue(self.user_admin.is_suspended(suspended_user.user))


class TestSuspendedUserAdmin(TestCase):
    def setUp(self):
        self.admin_site = admin.AdminSite()
        self.suspended_user_admin = SuspendedUserAdmin(SuspendedUser, self.admin_site)

    def test_list(self):
        expected_fields = [
            "get_username",
            "get_email",
            "reason",
            "suspended_at",
            "unsuspended_at",
            "is_suspended",
        ]
        self.assertEqual(self.suspended_user_admin.list_display, expected_fields)

    def test_filters(self):
        expected_filters = ["suspended_at", "unsuspended_at", "is_suspended"]
        self.assertEqual(self.suspended_user_admin.list_filter, expected_filters)

    def test_username(self):
        user = User.objects.create(username="test_user", email="ty@nyu.edu")
        suspended_user = SuspendedUser.objects.create(user=user)
        self.assertEqual(
            self.suspended_user_admin.get_username(suspended_user), "test_user"
        )

    def test_email(self):
        user = User.objects.create(username="test_user", email="ty@nyu.edu")
        suspended_user = SuspendedUser.objects.create(user=user)
        self.assertEqual(
            self.suspended_user_admin.get_email(suspended_user), "ty@nyu.edu"
        )


class TestBannedUserAdmin(TestCase):
    def setUp(self):
        self.admin_site = admin.AdminSite()
        self.banned_user_admin = BanneddUserAdmin(BannedUser, self.admin_site)

    def test_list(self):
        expected_fields = [
            "get_username",
            "get_email",
            "reason",
            "banned_at",
            "unban_at",
        ]
        self.assertEqual(self.banned_user_admin.list_display, expected_fields)

    def test_filters(self):
        expected_filters = ["banned_at", "unban_at"]
        self.assertEqual(self.banned_user_admin.list_filter, expected_filters)

    def test_username(self):
        user = User.objects.create(username="test_user", email="ty@nyu.edu")
        banned_user = BannedUser.objects.create(user=user)
        self.assertEqual(self.banned_user_admin.get_username(banned_user), "test_user")

    def test_email(self):
        user = User.objects.create(username="test_user", email="ty@nyu.edu")
        banned_user = BannedUser.objects.create(user=user)
        self.assertEqual(self.banned_user_admin.get_email(banned_user), "ty@nyu.edu")
