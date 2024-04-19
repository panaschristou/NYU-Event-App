from django.test import RequestFactory, TestCase
from django.urls import reverse, resolve
from backend import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from backend.models import Event, Review
import datetime
from django.http import HttpResponseRedirect


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
        cls.review = Review.objects.create(
            event=cls.event,
            user=cls.user,
            rating=5,
            review_text="This show is hilarious!",
            likes_count=0,
            reply_count=0,
        )

        # Generate UID and token for the user
        cls.uid = urlsafe_base64_encode(force_bytes(cls.user.pk))
        cls.token = default_token_generator.make_token(cls.user)

    def test_login_url_is_resolved(self):
        url = reverse("login")
        self.assertEqual(resolve(url).func, views.base.login_user)

    def test_register_url_is_resolved(self):
        url = reverse("register")
        self.assertEqual(resolve(url).func, views.base.register_user)

    def test_activate_url_is_resolved(self):
        url = reverse("activate", kwargs={"uidb64": self.uid, "token": self.token})
        self.assertEqual(resolve(url).func, views.base.activate)

    def test_event_detail_url_is_resolved(self):
        url = reverse("event_detail", kwargs={"event_id": self.event.pk})
        self.assertEqual(resolve(url).func, views.base.event_detail)

    def test_user_detail_url_is_resolved(self):
        user = get_user_model().objects.create(username="john_doe", password="12345")
        url = reverse("user_detail", kwargs={"username": user.username})
        self.assertEqual(resolve(url).func, views.base.user_detail)

    def test_search_results_url_is_resolved(self):
        url = reverse("search_results")
        self.assertEqual(resolve(url).func, views.base.search_results)

    def test_index_url_is_resolved(self):
        url = reverse("index")
        self.assertEqual(resolve(url).func, views.base.index_with_categories_view)

    def test_events_by_category_url_is_resolved(self):
        url = reverse("events_by_category", kwargs={"category": "music"})
        self.assertEqual(resolve(url).func, views.base.events_by_category)

    def test_reset_password_url(self):
        reset_password_url = reverse("reset_password")
        response = self.client.get(reset_password_url)
        self.assertEqual(response.status_code, 200)
        reset_password_sent_url = reverse("password_reset_done")
        response = self.client.get(reset_password_sent_url)
        self.assertEqual(response.status_code, 200)
        reset_password_complete_url = reverse("password_reset_complete")
        response = self.client.get(reset_password_complete_url)
        self.assertEqual(response.status_code, 200)

    def test_interst_list_url_is_resolved(self):
        url = reverse("interest_list")
        self.assertEqual(resolve(url).func, views.interest_list_handlers.interest_list)

    def test_profile_edit_url_is_resolved(self):
        url = reverse("profile_edit")
        self.assertEqual(resolve(url).func, views.profile_handlers.profile_edit)

    def test_search_history_url(self):
        view = resolve("/user/search_history/")
        self.assertEqual(view.func, views.base.search_history)

    def test_post_review_url(self):
        url = reverse("post_review", kwargs={"event_id": self.event.pk})
        self.assertEqual(resolve(url).func, views.review_handlers.post_review)

    def test_get_average_rating_url(self):
        url = reverse("get_average_rating", kwargs={"event_id": self.event.pk})
        self.assertEqual(resolve(url).func, views.review_handlers.get_average_rating)

    def test_get_reviews_for_event_url(self):
        url = reverse("event_reviews", kwargs={"event_id": self.event.pk})
        self.assertEqual(resolve(url).func, views.review_handlers.get_reviews_for_event)

    def test_like_review_url(self):
        url = reverse(
            "like_review",
            kwargs={"event_id": self.event.pk, "review_id": self.review.pk},
        )
        self.assertEqual(resolve(url).func, views.review_handlers.like_review)

    def test_unlike_review_url(self):
        url = reverse(
            "unlike_review",
            kwargs={"event_id": self.event.pk, "review_id": self.review.pk},
        )
        self.assertEqual(resolve(url).func, views.review_handlers.unlike_review)

    def test_delete_review_url(self):
        url = reverse(
            "delete_review",
            kwargs={"event_id": self.event.pk, "review_id": self.review.pk},
        )
        self.assertEqual(resolve(url).func, views.review_handlers.delete_review)

    def test_reply_to_review_url(self):
        url = reverse(
            "reply_to_review",
            kwargs={"event_id": self.event.pk, "review_id": self.review.pk},
        )
        self.assertEqual(resolve(url).func, views.review_handlers.reply_to_review)

    def test_get_replies_for_review_url(self):
        url = reverse(
            "display_replies",
            kwargs={"event_id": self.event.pk, "review_id": self.review.pk},
        )
        self.assertEqual(
            resolve(url).func, views.review_handlers.get_replies_for_review
        )
