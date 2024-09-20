# Forked Project from my Team's Project repo

NYU Event Application

# Coverage and Badges
Coverage and badges are shown in the original repo. The server on AWS has been shut down so the badges may not reflect that.


# How to start

`pip install -r installed_dependencies.txt`

Important: Pip freeze into installed_dependencies.txt, and leave requirements.txt empty

python manage.py runserver (To run on local host)

# Project Description
We created an event for NYU students using Django with Python, Javascript, PostGres, Bootstrap and Pusher to find events on Broadway and to connect with other students from NYU who are interested in similar events to discuss, chat about, review and rate those events. Project was deployed on Amazon AWS, used Travis CI/CD and Automated Testing using Coveralls. \
Feel free to look at the images below taken directly from the web application during operation.

# Project Features
- Login and Logout for Users and Admins.
- Profile page with user image, name etc.
- Database of events that can be updated programmatically through broadway website.
- Database of reviews, ratings  on event pages.
- Database of review replies from one user to another.
- Chat functionality. Chat between 2 users and group chat of all users for each individual event.
- Search and filter bar on main page for effective event and user search.
- Report feature for rude/inappropriate replies.
- Suspension and ban functionality in admin page.
- Lost password/username functionality.
- Emailing functionality to reset password/username or to be informed or account ban/suspension.
- Updated admin page to ban/suspend people, change passwords etc.

# Project Images
## Login
![Login Page](images/NYU-Event-Login.jpg)
## Logout
![Logout Page](images/NYU-Event-Logout.png)
## Profile
![Profile Page](images/NYU-Event-Profile.jpg)
## Interest List
![Interest List](images/NYU-Event-Interest-List.jpg)
## Review
![Write Review Page](images/NYU-Event-Review.jpg)
## Review Shown
![Review Page](images/NYU-Event-Review-Shown.jpg)
## Search Bar
![Search Bar in Index Page](images/NYU-Event-Search-Bar.jpg)
## Title Page
![Event Title Page](images/NYU-Event-Title-Page.jpg)
