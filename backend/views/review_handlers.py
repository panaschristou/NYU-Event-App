import json
import logging
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from backend.models import (
    Event,
    Review,
    SuspendedUser,
    ReplyToReview,
    Report,
    ReportReply,
)
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Avg
from django.db.models import F
from django.core.paginator import Paginator
from django.shortcuts import render

from backend.huggingface import censorbot
from datetime import datetime, timedelta
from backend.admin import send_notification_email

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
        reviews_per_page = 100

        reviews = Review.objects.filter(event__id=event_id).order_by("timestamp")

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
    if review.liked_by.filter(pk=user.pk).exists():
        return JsonResponse(
            {"error": "You have already liked this review."}, status=400
        )
    review.liked_by.add(user)
    review.likes_count += 1
    review.save()
    return JsonResponse({"success": True, "likes_count": review.likes_count})


@login_required
@require_POST
def unlike_review(request, event_id, review_id):
    review = get_object_or_404(Review, pk=review_id)
    user = request.user
    if not review.liked_by.filter(pk=user.pk).exists():
        return JsonResponse({"error": "You did not like this review."}, status=400)
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
    liked_by_users = reply.liked_by.all()
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
            "likes_count": reply.likes_count,
            "likes_by": [user.username for user in liked_by_users],
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
                    "likes_count": reply.likes_count,
                    "liked_by": list(reply.liked_by.values_list("username", flat=True)),
                }
            )
        return JsonResponse({"replies": replies_data})

    except Exception as e:
        print(e)
        return HttpResponseServerError("Server Error: {}".format(e))


@login_required
@require_POST
def like_reply(request, event_id, review_id, reply_id):
    replies = ReplyToReview.objects.filter(review__id=review_id)
    reply = get_object_or_404(replies, pk=reply_id)
    user = request.user
    if reply.liked_by.filter(pk=user.pk).exists():
        return JsonResponse(
            {"error": "You have already liked this review."}, status=400
        )

    reply.liked_by.add(user)
    reply.likes_count += 1
    reply.save()
    return JsonResponse({"success": True, "likes_count": reply.likes_count})


@login_required
@require_POST
def unlike_reply(request, event_id, review_id, reply_id):
    replies = ReplyToReview.objects.filter(review__id=review_id)
    reply = get_object_or_404(replies, pk=reply_id)
    user = request.user
    if not reply.liked_by.filter(pk=user.pk).exists():
        return JsonResponse({"error": "You did not like this review."}, status=400)

    reply.liked_by.remove(user)
    reply.likes_count = max(reply.likes_count - 1, 0)
    reply.save()
    return JsonResponse({"success": True, "likes_count": reply.likes_count})


@login_required
@require_POST
def delete_reply(request, event_id, review_id, reply_id):
    try:
        review = get_object_or_404(Review, pk=review_id)
        review.reply_count = review.reply_count - 1
        review.save()
        replies = ReplyToReview.objects.filter(review__id=review_id)
        reply = get_object_or_404(replies, pk=reply_id)
        reply.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
@require_POST
def report_review(request, review_id, event_id=None):
    try:
        # Parse JSON data from request body
        print(review_id)

        data = json.loads(request.body)
        print(request.body)
        review = get_object_or_404(Review, pk=review_id)

        # Check if the review has already been reported by this user
        if Report.objects.filter(review=review, reported_by=request.user).exists():
            return JsonResponse(
                {"success": False, "message": "You have already reported this review."}
            )

        # Extract title and description from the JSON data
        title = data.get("title")
        description = data.get("description")

        # Create a new report
        Report.objects.create(
            title=title,
            description=description,
            review=review,
            reported_by=request.user,
            reported_user=review.user,
        )
        review.is_reported = True
        review.save()

        subject = "Report Received"
        message = "Your report has been received. An admin will review your report and take appropriate action. Thank you for your patience."
        send_notification_email(request.user, subject, message)

        return JsonResponse(
            {"success": True, "message": "Report submitted successfully."}
        )
    except Exception as e:
        # Log the error for better debugging
        print(f"Error reporting review: {e}")
        return JsonResponse({"success": False, "message": str(e)})


@login_required
@require_POST
def reply_report(request, review_id, reply_id, event_id=None):
    try:
        # Parse JSON data from request body
        print(review_id)

        data = json.loads(request.body)
        print(request.body)
        review = get_object_or_404(Review, pk=review_id)
        reply = get_object_or_404(ReplyToReview, pk=reply_id)
        print(reply)

        # Check if the reply has already been reported by this user
        if ReportReply.objects.filter(reply=reply, reported_by=request.user).exists():
            return JsonResponse(
                {"success": False, "message": "You have already reported this reply."}
            )

        # Extract title and description from the JSON data
        title = data.get("title")
        description = data.get("description")

        # Create a new report
        ReportReply.objects.create(
            title=title,
            description=description,
            review=review,
            reply=reply,
            reported_by=request.user,
            reported_user=reply.fromUser,  # assuming reply.user is the one who made the reply
        )
        reply.is_reported = True
        reply.save()

        subject = "Report Received"
        message = "Your report has been received. An admin will review your report and take appropriate action. Thank you for your patience."
        send_notification_email(request.user, subject, message)

        return JsonResponse(
            {"success": True, "message": "Report submitted successfully."}
        )
    except Exception as e:
        # Log the error for better debugging
        print(f"Error reporting reply: {e}")
        return JsonResponse({"success": False, "message": str(e)})
