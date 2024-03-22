from django.test import TestCase
from django.contrib.auth.models import User
from backend.models import (
    Event,
    Review,
    UserEvent,
    Chat,
    SearchHistory,
    BannedUser,
    SuspendedUser,
)
from django.urls import reverse
import datetime


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
        # Set up data for the whole TestCase
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
