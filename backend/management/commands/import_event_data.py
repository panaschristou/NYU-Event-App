from django.core.management.base import BaseCommand, CommandError
from backend.models import Event
import json

class Command(BaseCommand):
    help = 'Import events from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing event data')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        with open(json_file_path, 'r') as file:
            events_data = json.load(file)
            for event_data in events_data:
                close_date = event_data['close_date'] if event_data['close_date'] else None
                Event.objects.create(
                    title=event_data['title'],
                    category=event_data['category'],
                    description=event_data['description'],
                    open_date=event_data['open_date'],
                    close_date=close_date,
                    location=event_data['location'],
                    availability=event_data['availability'],
                    external_link=event_data['external_link'],
                    image_url=event_data['image_url']
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported events'))
