from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.template.loader import render_to_string
from .models import Event
from .forms import UserRegistrationForm
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.db.models import Q


def index(request):
    events = Event.objects.all().order_by(
        "-title"
    )  # Assuming you want the newest events first
    return render(request, "index.html", {"events": events})


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    category = request.GET.get("category")
    return render(request, "event_detail.html", {"event": event, "category": category})


def user_detail(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    return render(request, "user_detail.html", {"user": user})


def search_results(request):
    search_query = request.GET.get("search_events", "").strip()
    search_type = request.GET.get("search_type", "Shows")
    User = get_user_model()
    events = Event.objects.none()
    users = User.objects.none()

    if search_query:
        if search_type == "Shows":
            events = Event.objects.filter(title__icontains=search_query)
            print(events)
        elif search_type == "Users":
            users = User.objects.filter(
                Q(username__icontains=search_query) | Q(email__icontains=search_query)
            )

    context = {
        "events": events if search_type == "Shows" else None,
        "users": users if search_type == "Users" else None,
        "search_query": search_query,
        "search_type": search_type,
    }
    return render(request, "search_results.html", context)


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
    categories = EVENT_CATEGORIES
    events = Event.objects.all()
    return render(request, "index.html", {"categories": categories, "events": events})


def events_by_category(request, category):
    events = Event.objects.filter(category__icontains=category)
    return render(
        request,
        "events_by_category.html",
        {"events": events, "current_category": category},
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


# Login existing user
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.success(request, ("There Was An Error Logging In, Try Again..."))
            return redirect("login")
    else:
        return render(request, "authenticate/login.html", {})
