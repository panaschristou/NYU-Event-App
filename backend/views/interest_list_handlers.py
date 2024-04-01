from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from ..models import Event, UserEvent
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


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


@require_POST
def add_interest(request, event_id):
    if (
        request.user.is_authenticated
        and not UserEvent.objects.filter(
            event_id=event_id, user_id=request.user.id
        ).exists()
    ):
        User = get_user_model()
        UserEvent.objects.create(
            event=Event.objects.get(pk=event_id),
            user=User.objects.get(pk=request.user.id),
            saved=True,
        )
        return JsonResponse({"message": "added to the interest list"})
    else:
        raise Http404("Operation Failed")


@require_POST
def remove_interest(request, event_id):
    if request.user.is_authenticated:
        User = get_user_model()
        (
            UserEvent.objects.get(
                event=Event.objects.get(pk=event_id),
                user=User.objects.get(pk=request.user.id),
            )
        ).delete()
        return JsonResponse({"message": "removed from the interest list"})
    else:
        raise Http404("Unauthorized Operation")
