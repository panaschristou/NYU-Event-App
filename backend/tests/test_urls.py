from django.test import TestCase
from django.urls import reverse, resolve
from backend import views
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from backend.models import Event
import datetime


class TestUrls(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create user and event for testing
        cls.user = User.objects.create_user(
            username="testuser@nyu.edu", password="12345Password!"
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

        # Generate UID and token for the user
        cls.uid = urlsafe_base64_encode(force_bytes(cls.user.pk))
        cls.token = default_token_generator.make_token(cls.user)

    def test_login_url_is_resolved(self):
        url = reverse("login")
        self.assertEqual(resolve(url).func, views.login_user)

    def test_register_url_is_resolved(self):
        url = reverse("register")
        self.assertEqual(resolve(url).func, views.register_user)

    def test_activate_url_is_resolved(self):
        url = reverse("activate", kwargs={"uidb64": self.uid, "token": self.token})
        self.assertEqual(resolve(url).func, views.activate)

    def test_event_detail_url_is_resolved(self):
        url = reverse("event_detail", kwargs={"event_id": self.event.pk})
        self.assertEqual(resolve(url).func, views.event_detail)

    def test_user_detail_url_is_resolved(self):
        user = get_user_model().objects.create(username="john_doe", password="12345")
        url = reverse("user_detail", kwargs={"username": user.username})
        self.assertEqual(resolve(url).func, views.user_detail)

    def test_search_results_url_is_resolved(self):
        url = reverse("search_results")
        self.assertEqual(resolve(url).func, views.search_results)

    def test_index_url_is_resolved(self):
        url = reverse("index")
        self.assertEqual(resolve(url).func, views.index_with_categories_view)

    def test_events_by_category_url_is_resolved(self):
        url = reverse("events_by_category", kwargs={"category": "music"})
        self.assertEqual(resolve(url).func, views.events_by_category)

    def test_interst_list_url_is_resolved(self):
        url = reverse("interest_list")
        self.assertEqual(resolve(url).func, views.interest_list)
