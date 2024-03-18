from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..forms import UpdateUserForm, UpdateProfileForm
from django.views.decorators.http import require_POST


@login_required
def profile_edit(request):
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile is updated successfully")
            return redirect(to="{% url 'profile_edit' %}")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
    return render(
        request,
        "profile_edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )
