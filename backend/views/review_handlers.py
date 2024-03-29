from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from backend.models import Event, Review, SuspendedUser
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.core.paginator import Paginator


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

    avg_rating_result = Review.objects.filter(event=event).aggregate(Avg("rating"))
    new_avg_rating = avg_rating_result["rating__avg"]

    if new_avg_rating is not None:
        new_avg_rating = round(new_avg_rating, 2)
        event.avg_rating = new_avg_rating
        event.save()

    return JsonResponse(
        {"success": True, "review_id": review.id, "new_avg_rating": new_avg_rating}
    )

def get_average_rating(request, event_id):
    reviews = Review.objects.filter(event__id=event_id)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    return JsonResponse({'avg_rating': average_rating})


def get_reviews_for_event(request, event_id):
    try:
        page_number = request.GET.get("page", 1)
        reviews_per_page = 10  # Set how many reviews you want per page

        reviews = Review.objects.filter(event__id=event_id).order_by("-timestamp")

        paginator = Paginator(reviews, reviews_per_page)
        page_obj = paginator.get_page(page_number)

        reviews_data = []
        for review in page_obj:
            reviews_data.append(
                {
                    "user": {
                        "username": review.user.username,
                        "profile": {
                            "avatar": review.user.profile.avatar.url
                            if review.user.profile.avatar
                            else None
                        },
                    },
                    "rating": review.rating,
                    "review_text": review.review_text,
                    "timestamp": review.timestamp.isoformat(),
                }
            )

        return JsonResponse(
            {
                "reviews": reviews_data,
                "has_next": page_obj.has_next(),
                "next_page_number": page_obj.next_page_number()
                if page_obj.has_next()
                else None,
            }
        )
    except Exception as e:
        print(e)
        return HttpResponseServerError("Server Error: {}".format(e))
