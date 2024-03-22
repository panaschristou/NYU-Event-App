from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from backend.models import Event, Review, SuspendedUser
from django.shortcuts import get_object_or_404


@login_required
@require_POST
def post_review(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user = request.user
    if SuspendedUser.objects.filter(user=user, is_suspended=True).exists():
        return JsonResponse(
            {
                "success": False,
                "message": "Your account is suspended. You cannot post a review.",
            }
        )
    rating = request.POST.get("rating")
    review_text = request.POST.get("review_text")
    review = Review(event=event, user=user, rating=rating, review_text=review_text)
    review.save()
    return JsonResponse({"success": True, "review_id": review.id})
