from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from backend.models import Event, Review
from django.shortcuts import get_object_or_404
from django.db.models import Avg


@login_required
@require_POST
def post_review(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user = request.user
    rating = request.POST.get("rating")
    review_text = request.POST.get("review_text")
    review = Review(event=event, user=user, rating=rating, review_text=review_text)
    review.save()

    avg_rating_result = Review.objects.filter(event=event).aggregate(Avg("rating"))
    new_avg_rating = avg_rating_result["rating__avg"]

    if new_avg_rating is not None:
        new_avg_rating = round(new_avg_rating, 2)
        event.avg_rating = new_avg_rating
        event.save()

    return JsonResponse(
        {"success": True, "review_id": review.id, "new_avg_rating": new_avg_rating}
    )
