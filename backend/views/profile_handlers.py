from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import UpdateUserForm, UpdateProfileForm
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model


@login_required
def profile_edit(request):
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("user_detail", username=request.user.username)
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
    return render(
        request,
        "profile_edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
@require_POST
def upload_avatar(request):
    User = get_user_model()
    user = User.objects.get(pk=request.user.id)
    file = request.FILES.get("file")
    print(file)
    if file:
        user.profile.avatar.save(file.name, file)
        return JsonResponse(
            {"status": "success", "message": "Avatar updated successfully."}, status=200
        )
    else:
        return JsonResponse(
            {"status": "error", "message": "No file provided."}, status=400
        )
