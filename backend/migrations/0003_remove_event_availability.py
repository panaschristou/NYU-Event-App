# Generated by Django 5.0.2 on 2024-03-08 00:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0002_alter_event_category_alter_event_location"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="availability",
        ),
    ]