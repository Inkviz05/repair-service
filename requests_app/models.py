from django.conf import settings
from django.db import models


class Request(models.Model):
    STATUS_NEW = "new"
    STATUS_ASSIGNED = "assigned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_ASSIGNED, "Assigned"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_DONE, "Done"),
        (STATUS_CANCELED, "Canceled"),
    ]

    client_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    address = models.CharField(max_length=500)
    problem_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Request #{self.id} - {self.client_name}"


class RequestEvent(models.Model):
    ACTION_CREATE = "create"
    ACTION_ASSIGN = "assign"
    ACTION_CANCEL = "cancel"
    ACTION_TAKE = "take"
    ACTION_COMPLETE = "complete"

    ACTION_CHOICES = [
        (ACTION_CREATE, "Create"),
        (ACTION_ASSIGN, "Assign"),
        (ACTION_CANCEL, "Cancel"),
        (ACTION_TAKE, "Take"),
        (ACTION_COMPLETE, "Complete"),
    ]

    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="events")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="request_events",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    from_status = models.CharField(max_length=20, choices=Request.STATUS_CHOICES, null=True, blank=True)
    to_status = models.CharField(max_length=20, choices=Request.STATUS_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.action} for request #{self.request_id}"
