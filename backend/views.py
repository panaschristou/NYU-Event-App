from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import User, Event
# from .forms import CustomUserCreationForm

# Create your views here.

def index(request):
    events = Event.objects.all().order_by('-title')  # Assuming you want the newest events first
    return render(request, 'index.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event_detail.html', {'event': event})

# def login(request, user):
# 	if request.method == "POST":
# 		username = request.POST['username']
# 		password = request.POST['password']
# 		user = authenticate(request, username=username, password=password)
# 		if user is not None:
# 			login(request, user)
# 			return redirect('home')
# 		else:
# 			messages.success(request, ("There Was An Error Logging In, Try Again..."))	
# 			return redirect('/login')	
# 	else:
# 		return render(request, 'authenticate/login.html', {})
	
def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('index')
		else:
			messages.success(request, ("There Was An Error Logging In, Try Again..."))	
			return redirect('login')
	else:
		return render(request, 'authenticate/login.html', {})



def register_user(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("Registration Successful!"))
			return redirect('login')
	else:
		form = UserCreationForm()

	return render(request, 'register.html', {
		'form':form,
		})

# def register(request):
# 	if request.method == "POST":
# 		form = CustomUserCreationForm(request.POST)
# 		# if form.is_valid():
# 			# user = User.objects.create(
#             #     username=form.cleaned_data['username'],
#             #     email=form.cleaned_data['email'],
#             #     password=form.cleaned_data['password1']
#             # )
# 			# user = authenticate(username=user.username, password=form.cleaned_data['password1'])
#             # login(request, user)
            
# 		if form.is_valid():
# 			user = User.objects.create(
#                 username=form.cleaned_data['username'],
#                 email=form.cleaned_data['email'],
#                 password=form.cleaned_data['password1']
#             )
# 			# form.save()
# 			# username = form.cleaned_data['username']
# 			# password = form.cleaned_data['password1']
# 			user = authenticate(username=user.username, password=form.cleaned_data['password1'])
# 			# user = authenticate(username=username, password=password)
# 			login(request, user)
# 			messages.success(request, ("Registration Successful!"))
# 			return redirect('login')
# 	else:
# 		form = CustomUserCreationForm()

# 	return render(request, 'register.html', {
# 		'form':form,
# 		})