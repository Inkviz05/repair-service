# Generated manually for test task.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Request",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("client_name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=32)),
                ("address", models.CharField(max_length=500)),
                ("problem_text", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("assigned", "Assigned"),
                            ("in_progress", "In progress"),
                            ("done", "Done"),
                            ("canceled", "Canceled"),
                        ],
                        default="new",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="RequestEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("create", "Create"),
                            ("assign", "Assign"),
                            ("cancel", "Cancel"),
                            ("take", "Take"),
                            ("complete", "Complete"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "from_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("new", "New"),
                            ("assigned", "Assigned"),
                            ("in_progress", "In progress"),
                            ("done", "Done"),
                            ("canceled", "Canceled"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "to_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("new", "New"),
                            ("assigned", "Assigned"),
                            ("in_progress", "In progress"),
                            ("done", "Done"),
                            ("canceled", "Canceled"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="request_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="requests_app.request",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
