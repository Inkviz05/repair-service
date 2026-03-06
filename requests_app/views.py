from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import RequestCreateForm
from .models import Request
from .services import (
    InvalidTransition,
    PermissionDenied,
    ServiceError,
    assign_request,
    cancel_request,
    complete_request,
    create_request,
    get_masters,
    is_dispatcher,
    is_master,
    take_request_in_work,
)


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Неверные логин или пароль.")
            return render(request, "login.html", status=401)
        login(request, user)
        return redirect("home")
    return render(request, "login.html")


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


@login_required
@require_GET
def home_view(request: HttpRequest) -> HttpResponse:
    if is_dispatcher(request.user):
        return redirect("dispatcher_dashboard")
    if is_master(request.user):
        return redirect("master_dashboard")
    return HttpResponseForbidden("У пользователя нет роли dispatcher/master.")


@login_required
@require_http_methods(["GET", "POST"])
def create_request_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RequestCreateForm(request.POST)
        if form.is_valid():
            request_obj = create_request(
                client_name=form.cleaned_data["client_name"],
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"],
                problem_text=form.cleaned_data["problem_text"],
                actor=request.user,
            )
            messages.success(request, f"Заявка #{request_obj.id} создана.")
            return redirect("create_request")
    else:
        form = RequestCreateForm()
    return render(request, "create_request.html", {"form": form})


@login_required
@require_GET
def dispatcher_dashboard_view(request: HttpRequest) -> HttpResponse:
    if not is_dispatcher(request.user):
        return HttpResponseForbidden("Доступ только для диспетчера.")

    status_filter = request.GET.get("status", "").strip()
    queryset = Request.objects.select_related("assigned_to")
    if status_filter in {choice[0] for choice in Request.STATUS_CHOICES}:
        queryset = queryset.filter(status=status_filter)

    context = {
        "requests": queryset.order_by("-created_at"),
        "status_filter": status_filter,
        "statuses": Request.STATUS_CHOICES,
        "masters": get_masters(),
    }
    return render(request, "dispatcher_dashboard.html", context)


@login_required
@require_POST
def assign_request_view(request: HttpRequest, request_id: int) -> HttpResponse:
    if not is_dispatcher(request.user):
        return HttpResponseForbidden("Доступ только для диспетчера.")

    request_obj = get_object_or_404(Request, id=request_id)
    master = get_object_or_404(User, id=request.POST.get("master_id"))
    try:
        assign_request(request_obj, master=master, actor=request.user)
        messages.success(request, f"Заявка #{request_obj.id} назначена мастеру {master.username}.")
    except (InvalidTransition, PermissionDenied, ServiceError) as exc:
        messages.error(request, str(exc))
    return redirect("dispatcher_dashboard")


@login_required
@require_POST
def cancel_request_view(request: HttpRequest, request_id: int) -> HttpResponse:
    if not is_dispatcher(request.user):
        return HttpResponseForbidden("Доступ только для диспетчера.")

    request_obj = get_object_or_404(Request, id=request_id)
    try:
        cancel_request(request_obj, actor=request.user)
        messages.success(request, f"Заявка #{request_obj.id} отменена.")
    except (InvalidTransition, PermissionDenied, ServiceError) as exc:
        messages.error(request, str(exc))
    return redirect("dispatcher_dashboard")


@login_required
@require_GET
def master_dashboard_view(request: HttpRequest) -> HttpResponse:
    if not is_master(request.user):
        return HttpResponseForbidden("Доступ только для мастера.")
    requests_qs = Request.objects.filter(assigned_to=request.user).order_by("-created_at")
    return render(request, "master_dashboard.html", {"requests": requests_qs})


@login_required
@require_POST
def take_request_view(request: HttpRequest, request_id: int) -> HttpResponse:
    if not is_master(request.user):
        return HttpResponseForbidden("Доступ только для мастера.")

    try:
        take_request_in_work(request_id=request_id, actor=request.user)
        messages.success(request, f"Заявка #{request_id} взята в работу.")
        return redirect("master_dashboard")
    except InvalidTransition as exc:
        return HttpResponse(str(exc), status=409)
    except PermissionDenied as exc:
        return HttpResponse(str(exc), status=403)


@login_required
@require_POST
def complete_request_view(request: HttpRequest, request_id: int) -> HttpResponse:
    if not is_master(request.user):
        return HttpResponseForbidden("Доступ только для мастера.")

    request_obj = get_object_or_404(Request, id=request_id)
    try:
        complete_request(request_obj, actor=request.user)
        messages.success(request, f"Заявка #{request_obj.id} завершена.")
    except (InvalidTransition, PermissionDenied, ServiceError) as exc:
        messages.error(request, str(exc))
    return redirect("master_dashboard")
