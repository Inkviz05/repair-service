from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("requests/new/", views.create_request_view, name="create_request"),
    path("dispatcher/", views.dispatcher_dashboard_view, name="dispatcher_dashboard"),
    path("dispatcher/requests/<int:request_id>/assign/", views.assign_request_view, name="assign_request"),
    path("dispatcher/requests/<int:request_id>/cancel/", views.cancel_request_view, name="cancel_request"),
    path("master/", views.master_dashboard_view, name="master_dashboard"),
    path("master/requests/<int:request_id>/take/", views.take_request_view, name="take_request"),
    path("master/requests/<int:request_id>/complete/", views.complete_request_view, name="complete_request"),
]
