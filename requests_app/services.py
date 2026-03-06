from dataclasses import dataclass

from django.contrib.auth.models import Group, User
from django.db import transaction
from django.utils import timezone

from .models import Request, RequestEvent


class ServiceError(Exception):
    pass


class InvalidTransition(ServiceError):
    pass


class PermissionDenied(ServiceError):
    pass


@dataclass(frozen=True)
class OperationResult:
    ok: bool
    message: str = ""


def is_master(user: User) -> bool:
    return user.groups.filter(name="master").exists()


def is_dispatcher(user: User) -> bool:
    return user.groups.filter(name="dispatcher").exists()


def get_masters():
    master_group = Group.objects.filter(name="master").first()
    if not master_group:
        return User.objects.none()
    return master_group.user_set.all().order_by("username")


def log_event(
    request_obj: Request,
    actor: User | None,
    action: str,
    from_status: str | None,
    to_status: str | None,
) -> None:
    RequestEvent.objects.create(
        request=request_obj,
        actor=actor,
        action=action,
        from_status=from_status,
        to_status=to_status,
    )


@transaction.atomic
def create_request(*, client_name: str, phone: str, address: str, problem_text: str, actor: User | None = None) -> Request:
    request_obj = Request.objects.create(
        client_name=client_name,
        phone=phone,
        address=address,
        problem_text=problem_text,
        status=Request.STATUS_NEW,
    )
    log_event(request_obj, actor, RequestEvent.ACTION_CREATE, None, Request.STATUS_NEW)
    return request_obj


@transaction.atomic
def assign_request(request_obj: Request, *, master: User, actor: User) -> OperationResult:
    if not is_dispatcher(actor):
        raise PermissionDenied("Only dispatcher can assign requests.")
    if not is_master(master):
        raise ServiceError("Assigned user is not a master.")
    if request_obj.status != Request.STATUS_NEW:
        raise InvalidTransition("Only new requests can be assigned.")

    old_status = request_obj.status
    request_obj.status = Request.STATUS_ASSIGNED
    request_obj.assigned_to = master
    request_obj.save(update_fields=["status", "assigned_to", "updated_at"])
    log_event(request_obj, actor, RequestEvent.ACTION_ASSIGN, old_status, Request.STATUS_ASSIGNED)
    return OperationResult(ok=True, message="Request assigned.")


@transaction.atomic
def cancel_request(request_obj: Request, *, actor: User) -> OperationResult:
    if not is_dispatcher(actor):
        raise PermissionDenied("Only dispatcher can cancel requests.")
    if request_obj.status == Request.STATUS_DONE:
        raise InvalidTransition("Done request cannot be canceled.")
    if request_obj.status == Request.STATUS_CANCELED:
        raise InvalidTransition("Request is already canceled.")

    old_status = request_obj.status
    request_obj.status = Request.STATUS_CANCELED
    request_obj.save(update_fields=["status", "updated_at"])
    log_event(request_obj, actor, RequestEvent.ACTION_CANCEL, old_status, Request.STATUS_CANCELED)
    return OperationResult(ok=True, message="Request canceled.")


@transaction.atomic
def take_request_in_work(*, request_id: int, actor: User) -> OperationResult:
    if not is_master(actor):
        raise PermissionDenied("Only master can take requests into work.")

    updated = (
        Request.objects.filter(
            id=request_id,
            status=Request.STATUS_ASSIGNED,
            assigned_to=actor,
        ).update(status=Request.STATUS_IN_PROGRESS, updated_at=timezone.now())
    )

    if updated == 0:
        raise InvalidTransition("Request already taken or not assigned to current master.")

    request_obj = Request.objects.get(id=request_id)
    log_event(request_obj, actor, RequestEvent.ACTION_TAKE, Request.STATUS_ASSIGNED, Request.STATUS_IN_PROGRESS)
    return OperationResult(ok=True, message="Request moved to in progress.")


@transaction.atomic
def complete_request(request_obj: Request, *, actor: User) -> OperationResult:
    if not is_master(actor):
        raise PermissionDenied("Only master can complete requests.")
    if request_obj.assigned_to_id != actor.id:
        raise PermissionDenied("Request is assigned to another master.")
    if request_obj.status != Request.STATUS_IN_PROGRESS:
        raise InvalidTransition("Only in_progress requests can be completed.")

    old_status = request_obj.status
    request_obj.status = Request.STATUS_DONE
    request_obj.save(update_fields=["status", "updated_at"])
    log_event(request_obj, actor, RequestEvent.ACTION_COMPLETE, old_status, Request.STATUS_DONE)
    return OperationResult(ok=True, message="Request completed.")
