import logging
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from backend.models import Event, Review, SuspendedUser, ReplyToReview
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Avg
from django.db.models import F
from django.core.paginator import Paginator
from django.shortcuts import render

from backend.huggingface import censorbot

logger = logging.getLogger(__name__)


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
    # if censorbot.detect_hate_speech(review_text)[0]["label"] == "hate":
    #     return JsonResponse(
    #         {
    #             "success": False,
    #             "message": "Your review contains hate speech. Please remove it and try again.",
    #         }
    #     )
    review = Review(event=event, user=user, rating=rating, review_text=review_text)

    review.likes_count = 0

    review.save()

    liked_by_users = review.liked_by.all()

    avg_rating_result = Review.objects.filter(event=event).aggregate(Avg("rating"))
    new_avg_rating = avg_rating_result["rating__avg"] or 0
    new_avg_rating = round(new_avg_rating, 2)
    event.avg_rating = new_avg_rating
    event.save()

    return JsonResponse(
        {
            "success": True,
            "review_id": review.id,
            "new_avg_rating": new_avg_rating,
            "user": {
                "username": user.username,
                "profile": {
                    "avatar": (user.profile.avatar.url if user.profile.avatar else None)
                },
            },
            "rating": review.rating,
            "review_text": review.review_text,
            "timestamp": review.timestamp.isoformat(),
            "likes_count": review.likes_count,
            "liked_by": [user.username for user in liked_by_users],
            "reply_count": review.reply_count,
        }
    )


def get_average_rating(request, event_id):
    reviews = Review.objects.filter(event__id=event_id)
    average_rating = reviews.aggregate(Avg("rating"))["rating__avg"]
    if average_rating is not None:
        return JsonResponse({"avg_rating": average_rating})
    else:
        return JsonResponse({"avg_rating": None})


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
                    "id": review.id,
                    "user": {
                        "username": review.user.username,
                        "profile": {
                            "avatar": (
                                review.user.profile.avatar.url
                                if review.user.profile.avatar
                                else None
                            )
                        },
                    },
                    "rating": review.rating,
                    "review_text": review.review_text,
                    "timestamp": review.timestamp.isoformat(),
                    "likes_count": review.likes_count,
                    "liked_by": list(
                        review.liked_by.values_list("username", flat=True)
                    ),
                    "reply_count": review.reply_count,
                }
            )

        return JsonResponse(
            {
                "reviews": reviews_data,
                "has_next": page_obj.has_next(),
                "next_page_number": (
                    page_obj.next_page_number() if page_obj.has_next() else None
                ),
            }
        )
    except Exception as e:
        print(e)
        return HttpResponseServerError("Server Error: {}".format(e))


@login_required
@require_POST
def like_review(request, event_id, review_id):
    review = get_object_or_404(Review, pk=review_id)
    user = request.user
    review.liked_by.add(user)
    review.likes_count += 1
    review.save()
    return JsonResponse({"success": True, "likes_count": review.likes_count})


@login_required
@require_POST
def unlike_review(request, event_id, review_id):
    review = get_object_or_404(Review, pk=review_id)
    user = request.user
    review.liked_by.remove(user)
    review.likes_count = max(review.likes_count - 1, 0)
    review.save()
    return JsonResponse({"success": True, "likes_count": review.likes_count})


@login_required
@require_POST
def delete_review(request, event_id, review_id):
    try:
        review = get_object_or_404(Review, pk=review_id)
        review.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def get_user_reviews(request, username):
    user = request.user
    reviews = Review.objects.filter(user=user).order_by("-timestamp")
    reviews_data = []
    for review in reviews:
        reviews_data.append(
            {
                "id": review.id,
                "event": {
                    "title": review.event.title,
                    "location": review.event.location,
                    "id": review.event.id,
                },
                "rating": review.rating,
                "review_text": review.review_text,
                "timestamp": review.timestamp.isoformat(),
                "likes_count": review.likes_count,
                "liked_by": list(review.liked_by.values_list("username", flat=True)),
            }
        )
    return render(request, "review_history.html", {"reviews": reviews_data})


@login_required
@require_POST
def delete_reviewhistory(request, review_id, username):
    try:
        review = get_object_or_404(Review, pk=review_id)
        review.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@require_POST
def reply_to_review(request, event_id, review_id):
    user = request.user
    if SuspendedUser.objects.filter(user=user, is_suspended=True).exists():
        return JsonResponse(
            {
                "success": False,
                "message": "Your account is suspended. You cannot post a reply.",
            }
        )
    review = get_object_or_404(Review, pk=review_id)
    reply_text = request.POST.get("reply_text")

    if not reply_text:
        return JsonResponse(
            {"success": False, "message": "Reply text is required."}, status=400
        )

    reply = ReplyToReview.objects.create(
        review=review, fromUser=user, toUser=review.user, reply_text=reply_text
    )
    review.reply_count = F("reply_count") + 1
    review.save()
    review.refresh_from_db(fields=["reply_count"])

    return JsonResponse(
        {
            "success": True,
            "reply_id": reply.id,
            "reply_text": reply.reply_text,
            "from_user": {
                "username": reply.fromUser.username,
                "profile": {
                    "avatar": (
                        reply.fromUser.profile.avatar.url
                        if reply.fromUser.profile.avatar
                        else None
                    )
                },
            },
            "to_user": review.user.username,
            "timestamp": reply.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "reply_count": review.reply_count,
        }
    )


def get_replies_for_review(request, event_id, review_id):
    try:
        replies = ReplyToReview.objects.filter(review__id=review_id).order_by(
            "-timestamp"
        )
        replies_data = []
        for reply in replies:
            replies_data.append(
                {
                    "id": reply.id,
                    "from_user": {
                        "username": reply.fromUser.username,
                        "profile": {
                            "avatar": (
                                reply.fromUser.profile.avatar.url
                                if reply.fromUser.profile.avatar
                                else None
                            )
                        },
                    },
                    "to_user": reply.toUser.username,
                    "reply_text": reply.reply_text,
                    "timestamp": reply.timestamp.isoformat(),
                }
            )
        return JsonResponse({"replies": replies_data})

    except Exception as e:
        print(e)
        return HttpResponseServerError("Server Error: {}".format(e))
