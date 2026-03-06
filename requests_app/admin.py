from django.contrib import admin

from .models import Request, RequestEvent


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("id", "client_name", "phone", "status", "assigned_to", "created_at")
    list_filter = ("status", "assigned_to")
    search_fields = ("client_name", "phone", "address")


@admin.register(RequestEvent)
class RequestEventAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "action", "actor", "from_status", "to_status", "created_at")
    list_filter = ("action", "from_status", "to_status")
