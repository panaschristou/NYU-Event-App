from django.test import TestCase, Client
from django.urls import reverse
from backend.models import Event, User, UserEvent, SearchHistory, Review
from django.core import mail
from django.contrib.messages import get_messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone
import json
from unittest.mock import mock_open, patch
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image


class EventViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser@nyu.edu", password="12345Password!"
        )

        # Create an event that is in the past
        self.past_event = Event.objects.create(
            title="Past Event",
            category="Musical",
            open_date=datetime.date(2022, 1, 1),
            close_date=datetime.date(2022, 1, 31),
            location="Past Location",
            external_link="http://www.example.com/past",
            image_url="https://www.example.com/image_past.jpg",
            avg_rating=0,
        )

        # Create an event that is current
        today = datetime.date.today()
        self.current_event = Event.objects.create(
            title="Current Event",
            category="Comedy",
            open_date=today - datetime.timedelta(days=10),
            close_date=today + datetime.timedelta(days=10),
            location="Current Location",
            external_link="http://www.example.com/current",
            image_url="https://www.example.com/image_current.jpg",
            avg_rating=0,
        )

        # Create an event that is in the future
        self.upcoming_event = Event.objects.create(
            title="Upcoming Event",
            category="Revival",
            open_date=datetime.date.today() + datetime.timedelta(days=30),
            close_date=datetime.date.today() + datetime.timedelta(days=60),
            location="Upcoming Location",
            external_link="http://www.example.com/upcoming",
            image_url="https://www.example.com/image_upcoming.jpg",
            avg_rating=0,
        )

        # Add reviews to create different average ratings and review counts
        Review.objects.create(
            event=self.current_event, user=self.user, rating=5, review_text="Great!"
        )
        Review.objects.create(
            event=self.current_event, user=self.user, rating=4, review_text="Good!"
        )

        Review.objects.create(
            event=self.upcoming_event, user=self.user, rating=3, review_text="Okay."
        )
        Review.objects.create(
            event=self.upcoming_event, user=self.user, rating=3, review_text="Decent."
        )
        Review.objects.create(
            event=self.upcoming_event, user=self.user, rating=3, review_text="Not bad."
        )

        # add current_event and upcoming_event to user interest list
        UserEvent.objects.create(event=self.current_event, user=self.user, saved=True)
        UserEvent.objects.create(event=self.upcoming_event, user=self.user, saved=True)

        self.category = "Musical, Comedy, Revival"

    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_event_detail_view(self):
        response = self.client.get(reverse("event_detail", args=(self.past_event.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "event_detail.html")

        response = self.client.get(reverse("event_detail", args=(9999,)))
        self.assertEqual(response.status_code, 404)

    def test_user_detail_view(self):
        url = reverse("user_detail", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_detail.html")
        self.assertEqual(response.context["detail_user"].username, "testuser@nyu.edu")

    def test_interest_list_view(self):
        self.client.login(username="testuser@nyu.edu", password="12345Password!")
        response = self.client.get(reverse("interest_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "interest_list.html")

        # Test that interestEvents contains the correct interested events of the user
        interestEvents = response.context["interestEvents"]
        testIds = [self.current_event.id, self.upcoming_event.id]
        for i in range(len(interestEvents)):
            self.assertEqual(interestEvents[i].id, testIds[i])

    def test_interest_list_add_and_remove_interest(self):
        self.client.login(username="testuser@nyu.edu", password="12345Password!")
        # Add interest
        response = self.client.post(
            reverse("interest_list_handlers.add_interest", args=(self.past_event.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            UserEvent.objects.filter(user=self.user, event=self.past_event).exists()
        )
        # Remove interest
        response = self.client.post(
            reverse(
                "interest_list_handlers.remove_interest", args=(self.past_event.id,)
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            UserEvent.objects.filter(user=self.user, event=self.past_event).exists()
        )

    def test_search_results_view(self):
        current_date = timezone.now().date()
        response = self.client.get(
            reverse("search_results") + "?search_events=Spamalot"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search_results.html")

        response = self.client.get(
            reverse("search_results") + "?search_events=Nonexistent"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search_results.html")

        # Test the availability filter for past events
        past_response = self.client.get(
            reverse("search_results") + "?search_events=Spamalot&availability=Past"
        )
        self.assertEqual(past_response.status_code, 200)
        self.assertTemplateUsed(past_response, "search_results.html")
        self.assertTrue(
            all(
                event.close_date < current_date
                for event in past_response.context["events"]
            )
        )

        # Test the availability filter for current events
        current_response = self.client.get(
            reverse("search_results") + "?search_events=Spamalot&availability=Current"
        )
        self.assertEqual(current_response.status_code, 200)
        self.assertTemplateUsed(current_response, "search_results.html")
        self.assertTrue(
            all(
                (
                    event.open_date <= current_date
                    and (event.close_date is None or event.close_date >= current_date)
                )
                for event in current_response.context["events"]
            )
        )

        # Test the availability filter for upcoming events
        upcoming_response = self.client.get(
            reverse("search_results") + "?search_events=Spamalot&availability=Upcoming"
        )
        self.assertEqual(upcoming_response.status_code, 200)
        self.assertTemplateUsed(upcoming_response, "search_results.html")
        self.assertTrue(
            all(
                event.open_date > current_date
                for event in upcoming_response.context["events"]
            )
        )

    def test_search_results_view_sort_by_average_rating(self):
        # Test sorting by average rating
        response = self.client.get(
            reverse("search_results") + "?sort_by=Average+Rating"
        )
        self.assertEqual(response.status_code, 200)
        events = list(response.context["events"])
        # Check that each event has a lower or equal avg_rating than the previous one
        self.assertTrue(
            all(
                events[i].avg_rating >= events[i + 1].avg_rating
                for i in range(len(events) - 1)
            )
        )

    def test_search_results_view_sort_by_popularity(self):
        # Test sorting by popularity (number of reviews)
        response = self.client.get(reverse("search_results") + "?sort_by=Popularity")
        self.assertEqual(response.status_code, 200)
        events = list(response.context["events"])
        # Assume events have a 'reviews' related_name for the related Review objects
        # Check that each event has a higher or equal number of reviews than the next one
        self.assertTrue(
            all(
                events[i].reviews.count() >= events[i + 1].reviews.count()
                for i in range(len(events) - 1)
            )
        )

    def test_index_with_categories_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_events_by_category_view(self):
        today = timezone.now().date()
        response = self.client.get(reverse("events_by_category", args=(self.category,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events_by_category.html")

        response = self.client.get(reverse("events_by_category", args=("Nonexistent",)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events_by_category.html")

        # Test the availability filter for past events
        past_response = self.client.get(
            reverse("events_by_category", args=(self.category,)) + "?availability=Past"
        )
        self.assertEqual(past_response.status_code, 200)
        self.assertTemplateUsed(past_response, "events_by_category.html")
        self.assertTrue(
            all(event.close_date < today for event in past_response.context["events"])
        )

        # Test the availability filter for current events
        current_response = self.client.get(
            reverse("events_by_category", args=(self.category,))
            + "?availability=Current"
        )
        self.assertEqual(current_response.status_code, 200)
        self.assertTemplateUsed(current_response, "events_by_category.html")
        self.assertTrue(
            all(
                (
                    event.open_date <= today
                    and (event.close_date is None or event.close_date >= today)
                )
                for event in current_response.context["events"]
            )
        )

    def test_events_by_category_view_sort_by_average_rating(self):
        # Test sorting by average rating within a specific category
        response = self.client.get(
            reverse("events_by_category", args=(self.category,))
            + "?sort_by=Average+Rating"
        )
        self.assertEqual(response.status_code, 200)
        events = list(response.context["events"])
        # Check that each event has a lower or equal avg_rating than the previous one within the category
        self.assertTrue(
            all(
                events[i].avg_rating >= events[i + 1].avg_rating
                for i in range(len(events) - 1)
            )
        )

    def test_events_by_category_view_sort_by_popularity(self):
        today = timezone.now().date()
        # Test sorting by popularity (number of reviews) within a specific category
        response = self.client.get(
            reverse("events_by_category", args=(self.category,)) + "?sort_by=Popularity"
        )
        self.assertEqual(response.status_code, 200)
        events = list(response.context["events"])
        # Check that each event has a higher or equal number of reviews than the next one within the category
        self.assertTrue(
            all(
                events[i].reviews.count() >= events[i + 1].reviews.count()
                for i in range(len(events) - 1)
            )
        )

        # Test the availability filter for upcoming events
        upcoming_response = self.client.get(
            reverse("events_by_category", args=(self.category,))
            + "?availability=Upcoming"
        )
        self.assertEqual(upcoming_response.status_code, 200)
        self.assertTemplateUsed(upcoming_response, "events_by_category.html")
        self.assertTrue(
            all(
                event.open_date > today for event in upcoming_response.context["events"]
            )
        )

    def test_register_user_view(self):
        form_data = {
            "username": "newuser@nyu.edu",
            "email": "newuser@nyu.edu",
            "password1": "testpassworD1!",
            "password2": "testpassworD1!",
        }
        response = self.client.post(reverse("register"), form_data)

        # Check redirection to login page after registration
        self.assertRedirects(response, reverse("login"))

        # Check if an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Activate your user account")

        # Check if user is not active before activation
        new_user = User.objects.get(username="newuser@nyu.edu")
        self.assertFalse(new_user.is_active)

    def test_account_activation(self):
        # Prepare the token and uid
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        # Activation with correct token
        response = self.client.get(reverse("activate", args=(uid, token)))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertRedirects(response, reverse("login"))

        # Deactivate the user for the test
        self.user.is_active = False
        self.user.save()

        # Activation with incorrect token
        response = self.client.get(reverse("activate", args=(uid, "wrong-token")))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_login_user_view(self):
        # Test login with correct credentials
        response = self.client.post(
            reverse("login"),
            {"username": "testuser@nyu.edu", "password": "12345Password!"},
        )
        self.assertRedirects(response, reverse("index"))

        # Test login with incorrect credentials
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "wrong"}
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "There Was An Error Logging In, Try Again..."
        )

    def test_post_review(self):
        self.client.login(username="testuser@nyu.edu", password="12345Password!")

        url = reverse("post_review", kwargs={"event_id": self.current_event.id})

        review_data = {"rating": 5, "review_text": "Great event!"}

        response = self.client.post(url, review_data)

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)

        self.assertTrue(response_data["success"])
        self.assertIsNotNone(response_data["review_id"])

        review = Review.objects.get(pk=response_data["review_id"])
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.event, self.current_event)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, "Great event!")


class ProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="12345Password!"
        )
        self.client.login(username="testuser", password="12345Password!")

    def test_profile_edit_view(self):
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile_edit.html")
        self.assertIn("user_form", response.context)
        self.assertIn("profile_form", response.context)

    def test_profile_edit_post(self):
        image = Image.new("RGB", (100, 100), color=(73, 109, 137))
        temp_file = BytesIO()
        image.save(temp_file, "png")
        temp_file.seek(0)
        form_data = {
            "first_name": "new_first_name",
            "last_name": "new_last_name",
            "description": "new description",
            "avatar": SimpleUploadedFile(
                "testuser.png", temp_file.read(), content_type="image/png"
            ),
        }

        response = self.client.post(reverse("profile_edit"), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Refresh the user object from the database
        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "new_first_name")
        self.assertEqual(self.user.last_name, "new_last_name")
        # Assuming 'profile' is a OneToOneField linked to the User model
        self.assertEqual(self.user.profile.description, "new description")
        self.assertEqual(self.user.profile.avatar.name, "profile_images/testuser.png")


class SearchHistoryViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@nyu.edu", password="testpassword"
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")
        self.search_history1 = SearchHistory.objects.create(
            user=self.user, search="Test Search 1", search_type="Shows"
        )
        self.search_history2 = SearchHistory.objects.create(
            user=self.user, search="Test Search 2", search_type="Shows"
        )

    def test_access_search_history(self):
        response = self.client.get(reverse("search_history"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search_history.html")
        self.assertContains(response, "Test Search 1")
        self.assertContains(response, "Test Search 2")

    def test_delete_search(self):
        response = self.client.post(
            reverse("delete_search", args=[self.search_history1.id])
        )
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertNotIn(self.search_history1, SearchHistory.objects.all())

    def test_clear_history(self):
        response = self.client.post(reverse("clear_history"))
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertFalse(SearchHistory.objects.filter(user=self.user).exists())
