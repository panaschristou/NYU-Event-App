from pusher import Pusher
from django.http import JsonResponse
from django.conf import settings
import pusher
from django.views.decorators.csrf import csrf_exempt


# Initialize Pusher
# pusher = Pusher(
#     app_id=settings.PUSHER_APP_ID,
#     key=settings.PUSHER_KEY,
#     secret=settings.PUSHER_SECRET,
#     cluster=settings.PUSHER_CLUSTER,
#     ssl=True
# )

pusher_client = Pusher(
  app_id='1773977',
  key='e44f77643020ff731b4f',
  secret='064da109d46ae1fd75ee',
  cluster='mt1',
  ssl=True
)

@csrf_exempt
def pusher_authentication(request):
    if request.method == 'POST':
        channel_name = request.POST.get('channel_name')
        socket_id = request.POST.get('socket_id')
        auth = pusher_client.authenticate(
            channel=channel_name,
            socket_id=socket_id
        )
        return JsonResponse(auth)

