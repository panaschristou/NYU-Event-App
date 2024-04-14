import re
from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from ..models import (
    Event,
    UserEvent,
    SearchHistory,
    Review,
    BannedUser,
    SuspendedUser,
    User,
    Room3,
)
from ..forms import UserRegistrationForm
from ..tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg, Count, Q, Value, FloatField
from django.db.models.functions import Coalesce

EVENT_CATEGORIES = [
    "Musical",
    "Original",
    "Play",
    "Drama",
    "Revival",
    "Comedy",
    "Puppets",
]


def index_with_categories_view(request):
    availability_filter = request.GET.get("availability", "All")
    sort_by = request.GET.get("sort_by", "")
    now = timezone.now()

    events = Event.objects.all().order_by("title")

    # Filter events based on availability
    if availability_filter == "Past":
        events = events.filter(close_date__isnull=False, close_date__lt=now)
    elif availability_filter == "Current":
        events = events.filter(
            Q(open_date__lte=now, close_date__gte=now)
            | Q(open_date__lte=now, close_date__isnull=True)
        )
    elif availability_filter == "Upcoming":
        events = events.filter(open_date__gt=now)

    # Sort events based on user selection
    if sort_by == "Average Rating":
        events = events.annotate(
            adjusted_avg_rating=Coalesce(
                Avg("reviews__rating"), Value(0), output_field=FloatField()
            )
        ).order_by("-adjusted_avg_rating")
    elif sort_by == "Popularity":
        events = events.annotate(review_count=Count("reviews")).order_by(
            "-review_count"
        )

    categories = EVENT_CATEGORIES

    context = {
        "events": events,
        "categories": categories,
        "current_availability": availability_filter,
        "current_sort": sort_by,
    }
    return render(request, "index.html", context)


def event_detail(request, event_id):
    loggedIn = request.user.is_authenticated
    event = get_object_or_404(Event, pk=event_id)

    pattern = r"[^a-zA-Z0-9\s]"
    cleaned_title = re.sub(pattern, "", event.title)
    title_split = cleaned_title.split()
    room_slug = ""
    if len(title_split) >= 3:
        room_slug = "_".join(title_split[:3])
    else:
        room_slug = "_".join(title_split[:])

    room_slug = room_slug.lower()

    interested = False
    if loggedIn:
        interested = UserEvent.objects.filter(
            event=event,
            user=request.user,
        ).exists()

    avg_rating_result = Review.objects.filter(event=event).aggregate(Avg("rating"))
    avg_rating = avg_rating_result["rating__avg"]

    if avg_rating is not None:
        avg_rating = round(avg_rating, 2)
        event.avg_rating = avg_rating
        event.save()
    else:
        event.avg_rating = avg_rating
        event.save()

    return render(
        request,
        "event_detail.html",
        {
            "event_id": event_id,
            "event": event,
            "loggedIn": loggedIn,
            "interested": interested,
            "avg_rating": avg_rating,
            "room_slug": room_slug,
        },
    )


def user_detail(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    return render(request, "user_detail.html", {"detail_user": user})


@login_required
def interest_list(request):
    User = get_user_model()
    interestList = []
    if request.user.id:
        interestList = UserEvent.objects.filter(
            user=User.objects.get(pk=request.user.id),
        )
    interestEventIds = [userEvent.event_id for userEvent in interestList]
    interestEvents = Event.objects.filter(id__in=interestEventIds)
    return render(request, "interest_list.html", {"interestEvents": interestEvents})


def search_results(request):
    search_query = request.GET.get("search_events", "").strip()
    search_type = request.GET.get("search_type", "Shows")
    sort_by = request.GET.get("sort_by", "")
    User = get_user_model()

    availability_filter = request.GET.get("availability", "All")
    now = timezone.now()

    if search_query:
        events = Event.objects.filter(title__icontains=search_query)
    else:
        events = Event.objects.all()

    users = User.objects.none()

    if search_query:
        if request.user.is_authenticated:
            SearchHistory.objects.create(
                user=request.user, search=search_query, search_type=search_type
            )
        if search_type == "Shows":
            if availability_filter != "All":
                if availability_filter == "Past":
                    events = events.filter(close_date__isnull=False, close_date__lt=now)
                elif availability_filter == "Current":
                    events = events.filter(
                        Q(open_date__lte=now, close_date__gte=now)
                        | Q(open_date__lte=now, close_date__isnull=True)
                    )
            elif availability_filter == "Upcoming":
                events = events.filter(open_date__gt=now)
        elif search_type == "Users":
            users = User.objects.filter(
                Q(username__icontains=search_query) | Q(email__icontains=search_query)
            )

    if sort_by == "Average Rating":
        events = events.annotate(
            adjusted_avg_rating=Coalesce(
                Avg("reviews__rating"), Value(0), output_field=FloatField()
            )
        ).order_by("-adjusted_avg_rating")
    elif sort_by == "Popularity":
        events = events.annotate(review_count=Count("reviews")).order_by(
            "-review_count"
        )

    context = {
        "events": events if search_type == "Shows" else None,
        "users": users if search_type == "Users" else None,
        "search_query": search_query,
        "search_type": search_type,
    }
    return render(request, "search_results.html", context)


def search_history(request):
    user = request.user
    search_history = SearchHistory.objects.filter(user=user).order_by("-timestamp")
    return render(request, "search_history.html", {"search_history": search_history})


def delete_search_view(request, search_id):
    search = SearchHistory.objects.get(id=search_id)
    if search.user == request.user:
        search.delete()
    return redirect("search_history")


def clear_history_view(request):
    SearchHistory.objects.filter(user=request.user).delete()
    return redirect("search_history")


def recent_searches(request):
    if request.user.is_authenticated:
        recent_searches = SearchHistory.objects.filter(user=request.user).order_by(
            "-timestamp"
        )[
            :5
        ]  # Get the last 5 searches
        searches = [search.search for search in recent_searches]
        return JsonResponse({"recent_searches": searches})
    return JsonResponse({"recent_searches": []})


def events_by_category(request, category):
    categories = EVENT_CATEGORIES
    availability_filter = request.GET.get("availability", "All")
    now = timezone.now()
    sort_by = request.GET.get("sort_by", "")

    events = Event.objects.filter(category__icontains=category)

    if availability_filter != "All":
        if availability_filter == "Past":
            events = events.filter(close_date__isnull=False, close_date__lt=now)
        elif availability_filter == "Current":
            events = events.filter(
                Q(open_date__lte=now, close_date__gte=now)
                | Q(open_date__lte=now, close_date__isnull=True)
            )
        elif availability_filter == "Upcoming":
            events = events.filter(open_date__gt=now)

    if sort_by == "Average Rating":
        events = events.annotate(
            adjusted_avg_rating=Coalesce(
                Avg("reviews__rating"), Value(0), output_field=FloatField()
            )
        ).order_by("-adjusted_avg_rating")
    elif sort_by == "Popularity":
        events = events.annotate(review_count=Count("reviews")).order_by(
            "-review_count"
        )

    return render(
        request,
        "events_by_category.html",
        {"events": events, "categories": categories, "current_category": category},
    )


# This code snippet is called once the verification link is accessed by the user, to confirm the validity of the link.
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login your account.",
        )
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect("login")


# This code snippet is responsible for generating and sending the verification email.
def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account"
    message = render_to_string(
        "template_activate_account.html",
        {
            "user": user.username,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(
            request,
            f"Dear {user}, please go to you email {to_email} inbox and click on \
                received activation link to confirm and complete the registration. Note: Check your spam folder.",
        )
    else:
        messages.error(
            request,
            f"Problem sending email to {to_email}, check if you typed it correctly.",
        )


# Register new user
def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get("email"))
            return redirect("login")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegistrationForm()
        #    form = {}

    return render(
        request=request, template_name="register.html", context={"form": form}
    )


# Delete current user
@login_required
@require_POST
def delete_user(request):
    User = get_user_model()
    user = User.objects.filter(id=request.user.id).first()
    if user:
        user.delete()
    return JsonResponse({"message": "account has been deleted"})


# Login existing user
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        remember_me = request.POST.get("remember_me")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            if user.check_password(password):
                # Check if the user is banned
                try:
                    BannedUser.objects.get(user=user)
                    messages.error(request, "Your account has been banned.")
                    return redirect("login")
                except BannedUser.DoesNotExist:
                    pass

                if user.is_active:
                    login(request, user)
                    if remember_me:
                        request.session.set_expiry(604800)
                    else:
                        request.session.set_expiry(0)
                    return redirect("index")
                else:
                    messages.error(
                        request,
                        "Account is not authenticated. Check your email and authenticate before logging in.",
                    )
                    return redirect("login")
            else:
                messages.error(request, "Invalid username or password.")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    else:
        return render(request, "authenticate/login.html", {})


def import_rooms(request):
    event_titles = Event.objects.values_list("title", flat=True)

    pattern = r"[^a-zA-Z0-9\s]"

    for title in event_titles:
        cleaned_title = re.sub(pattern, "", title)

        title_split = cleaned_title.split()

        room_name = ""

        if len(title_split) >= 3:
            room_name = "_".join(title_split[:3])
        else:
            room_name = "_".join(title_split[:])

        Room3.objects.create(name=title, slug=room_name.lower())
