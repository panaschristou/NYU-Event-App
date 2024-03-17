from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..forms import UpdateUserForm, UpdateProfileForm
from django.views.decorators.http import require_POST


@login_required
@require_POST
def profile(request):
    user_form = UpdateUserForm(request.POST, instance=request.user)
    profile_form = UpdateProfileForm(
        request.POST, request.FILES, instance=request.user.profile
    )
    if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Profile is updated successfully")
        return redirect(to="profile-edit")
