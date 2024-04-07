from django.test import TestCase
from unittest.mock import mock_open, patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from backend.models import (
    Event,
    Review,
    UserEvent,
    Chat,
    SearchHistory,
    BannedUser,
    SuspendedUser,
    Profile,
    ReplyToReview,
)
from django.urls import reverse
import datetime


class ProfileModalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test data for Profile model
        cls.user = User.objects.create_user(
            username="testuser", email="testuser@nyu.edu", password="12345"
        )
        cls.profile = Profile.objects.get(
            user_id=cls.user.id,
        )
        cls.profile.description = "A broadway lover from NYU"
        mock_file = mock_open(read_data=b"file_content")
        with patch("builtins.open", mock_file):
            cls.profile.avatar = SimpleUploadedFile(
                name="testuser.jpg",
                content=open("profile_images/testuser.jpg", "rb").read(),
                content_type="image/png",
            )
        cls.profile.save()

    def test_profile_attributes(self):
        # Test fetching the review from the database
        profile = Profile.objects.get(id=self.profile.id)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.description, "A broadway lover from NYU")
        self.assertEqual(profile.avatar.name, "profile_images/testuser.jpg")


class UserEventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", email="testuser@nyu.edu", password="12345"
        )
        cls.event = Event.objects.create(
            title="Spamalot",
            category="Musical, Comedy, Revival, Broadway",
            description="Lovingly ripped from the film classic",
            open_date=datetime.date(2023, 11, 16),
            close_date=datetime.date(2023, 10, 31),
            location="St. James Theatre, 246 West 44th Street, Between Broadway and 8th Avenue",
            external_link="http://www.broadway.org/shows/details/spamalot,812",
            image_url="https://www.broadway.org/logos/shows/spamalot-2023.jpg",
            avg_rating=0,  # Assuming initial avg_rating
        )
        cls.user_event = UserEvent.objects.create(
            saved=True,
            user=cls.user,
            event=cls.event,
        )

    def test_user_event_attributes(self):
        user_event = UserEvent.objects.get(id=self.user_event.id)
        self.assertEqual(user_event.user, self.user)
        self.assertEqual(user_event.event, self.event)
        self.assertTrue(user_event.saved)


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test data for Event model
        cls.event = Event.objects.create(
            title="Spamalot",
            category="Musical, Comedy, Revival, Broadway",
            description="Lovingly ripped from the film classic",
            open_date=datetime.date(2023, 11, 16),
            close_date=datetime.date(2023, 10, 31),
            location="St. James Theatre, 246 West 44th Street, Between Broadway and 8th Avenue",
            external_link="http://www.broadway.org/shows/details/spamalot,812",
            image_url="https://www.broadway.org/logos/shows/spamalot-2023.jpg",
            avg_rating=0,  # Assuming initial avg_rating
        )

    def test_event_attributes(self):
        # Fetch the event from the database
        event = Event.objects.get(title="Spamalot")

        # Check that the event's attributes match what was set up in the database
        self.assertEqual(event.title, "Spamalot")
        self.assertEqual(event.category, "Musical, Comedy, Revival, Broadway")
        self.assertEqual(event.description, "Lovingly ripped from the film classic")
        self.assertEqual(event.open_date, datetime.date(2023, 11, 16))
        self.assertEqual(event.close_date, datetime.date(2023, 10, 31))
        self.assertEqual(
            event.location,
            "St. James Theatre, 246 West 44th Street, Between Broadway and 8th Avenue",
        )
        self.assertEqual(
            event.external_link, "http://www.broadway.org/shows/details/spamalot,812"
        )
        self.assertEqual(
            event.image_url, "https://www.broadway.org/logos/shows/spamalot-2023.jpg"
        )
        self.assertEqual(event.avg_rating, 0)


class ReviewModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = Event.objects.create(
            title="Spamalot",
            category="Musical, Comedy, Revival, Broadway",
            description="Lovingly ripped from the film classic",
            open_date=datetime.date(2023, 11, 16),
            close_date=datetime.date(2023, 10, 31),
            location="St. James Theatre, 246 West 44th Street, Between Broadway and 8th Avenue",
            external_link="http://www.broadway.org/shows/details/spamalot,812",
            image_url="https://www.broadway.org/logos/shows/spamalot-2023.jpg",
            avg_rating=0,
        )
        cls.user = User.objects.create_user(username="testuser", password="12345")
        cls.event = Event.objects.get(title="Spamalot")
        cls.review = Review.objects.create(
            event=cls.event,
            user=cls.user,
            rating=5,
            review_text="It was a fantastic show!",
        )

    def test_review_attributes(self):
        # Test fetching the review from the database
        review = Review.objects.get(id=self.review.id)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, "It was a fantastic show!")
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.event, self.event)
        self.assertEqual(review.likes_count, 0)
        self.assertEqual(review.reply_count, 0)
        self.assertFalse(review.liked_by.exists())

    def test_likes_count_default_value(self):
        # Test the default value of likes_count
        self.assertEqual(self.review.likes_count, 0)

    def test_reply_count_default_value(self):
        # Test the default value of reply_count
        self.assertEqual(self.review.reply_count, 0)


class ReplyToReviewModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.from_user = User.objects.create_user(username="fromuser", password="12345")
        cls.to_user = User.objects.create_user(username="touser", password="12345")
        cls.event = Event.objects.create(
            title="Spamalot",
            category="Musical, Comedy, Revival, Broadway",
            description="Lovingly ripped from the film classic",
            open_date=datetime.date(2023, 11, 16),
            close_date=datetime.date(2023, 10, 31),
            location="St. James Theatre, 246 West 44th Street, Between Broadway and 8th Avenue",
            external_link="http://www.broadway.org/shows/details/spamalot,812",
            image_url="https://www.broadway.org/logos/shows/spamalot-2023.jpg",
            avg_rating=0,
        )
        cls.review = Review.objects.create(
            event=cls.event,
            user=cls.to_user,
            rating=4,
            review_text="Nice event!",
        )
        cls.reply = ReplyToReview.objects.create(
            review=cls.review,
            fromUser=cls.from_user,
            toUser=cls.to_user,
            reply_text="Thank you!",
        )

    def test_reply_attributes(self):
        # Test fetching the reply from the database
        reply = ReplyToReview.objects.get(id=self.reply.id)
        self.assertEqual(reply.review, self.review)
        self.assertEqual(reply.fromUser, self.from_user)
        self.assertEqual(reply.toUser, self.to_user)
        self.assertEqual(reply.reply_text, "Thank you!")
        # The timestamp is automatically set to the current time; we can't test its exact value,
        # but we can check that it's been set.
        self.assertIsNotNone(reply.timestamp)

    def test_str_method(self):
        # The __str__ method should return the text of the reply
        self.assertEqual(str(self.reply), "Thank you!")


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", email="testuser@nyu.edu", password="testpassword"
        )

    def test_user_attributes(self):
        # Fetch the user and check attributes
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "testuser@nyu.edu")


class SearchHistoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for the test
        cls.user = User.objects.create_user(
            username="testuser", email="testuser@nyu.edu", password="testpassword"
        )
        # Create a SearchHistory object for the test
        cls.search_history = SearchHistory.objects.create(
            user=cls.user, search="Django Testing", search_type="Shows"
        )

    def test_search_history_content(self):
        # Test the content of the SearchHistory object
        self.assertEqual(self.search_history.user, self.user)
        self.assertEqual(self.search_history.search, "Django Testing")
        self.assertEqual(self.search_history.search_type, "Shows")

    def test_search_history_str(self):
        # Test the string representation of the SearchHistory object
        self.assertEqual(str(self.search_history.search), "Django Testing")


class SuspendedUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", email="testuser@nyu.edu", password="testpassword"
        )
        cls.suspended_user = SuspendedUser.objects.create(
            user=cls.user, reason="Test reason", is_suspended=True
        )

    def test_suspended_user_attributes(self):
        suspended_user = SuspendedUser.objects.get(user=self.user)
        self.assertEqual(suspended_user.user, self.user)
        self.assertEqual(suspended_user.reason, "Test reason")
        self.assertTrue(suspended_user.is_suspended)
        self.assertIsNotNone(suspended_user.suspended_at)
        self.assertIsNone(suspended_user.unsuspended_at)

    def test_unsuspend_user(self):
        self.suspended_user.unsuspend_user()
        with self.assertRaises(SuspendedUser.DoesNotExist):
            SuspendedUser.objects.get(user=self.user)


class BannedUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@nyu.edu",
            password="testpassword",
            is_active=False,
        )
        cls.banned_user = BannedUser.objects.create(user=cls.user, reason="Test reason")

    def test_banned_user_attributes(self):
        banned_user = BannedUser.objects.get(user=self.user)
        self.assertEqual(banned_user.user, self.user)
        self.assertEqual(banned_user.reason, "Test reason")
        self.assertFalse(self.user.is_active)
        self.assertIsNotNone(banned_user.banned_at)
        self.assertIsNone(banned_user.unban_at)

    def test_unban_user(self):
        self.banned_user.unban_user()
        with self.assertRaises(BannedUser.DoesNotExist):
            BannedUser.objects.get(user=self.user)


class ChatModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.sender = User.objects.create_user(username="sender", password="testpass123")
        cls.receiver = User.objects.create_user(
            username="receiver", password="testpass123"
        )
        cls.chat = Chat.objects.create(
            sender=cls.sender, receiver=cls.receiver, message="Hello"
        )

    def test_chat_content(self):
        self.assertEqual(self.chat.sender, self.sender)
        self.assertEqual(self.chat.receiver, self.receiver)
        self.assertEqual(self.chat.message, "Hello")
