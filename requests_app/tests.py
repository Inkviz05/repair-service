from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Request


class BaseTestCase(TestCase):
    def setUp(self):
        self.dispatcher_group = Group.objects.create(name="dispatcher")
        self.master_group = Group.objects.create(name="master")

        self.dispatcher = User.objects.create_user(username="disp", password="pass123")
        self.dispatcher.groups.add(self.dispatcher_group)

        self.master1 = User.objects.create_user(username="master1", password="pass123")
        self.master1.groups.add(self.master_group)

        self.master2 = User.objects.create_user(username="master2", password="pass123")
        self.master2.groups.add(self.master_group)


class RequestFlowTests(BaseTestCase):
    def test_create_request_sets_new_status(self):
        self.client.force_login(self.dispatcher)
        response = self.client.post(
            reverse("create_request"),
            {
                "client_name": "Client",
                "phone": "+79000000000",
                "address": "Address 1",
                "problem_text": "Broken socket",
            },
        )
        self.assertEqual(response.status_code, 302)
        req = Request.objects.get()
        self.assertEqual(req.status, Request.STATUS_NEW)
        self.assertIsNone(req.assigned_to)

    def test_dispatcher_can_assign_and_cancel_with_rules(self):
        self.client.force_login(self.dispatcher)
        req = Request.objects.create(
            client_name="Client",
            phone="+79000000001",
            address="Addr",
            problem_text="Issue",
            status=Request.STATUS_NEW,
        )
        assign_response = self.client.post(
            reverse("assign_request", kwargs={"request_id": req.id}),
            {"master_id": self.master1.id},
        )
        self.assertEqual(assign_response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, Request.STATUS_ASSIGNED)
        self.assertEqual(req.assigned_to_id, self.master1.id)

        cancel_response = self.client.post(reverse("cancel_request", kwargs={"request_id": req.id}))
        self.assertEqual(cancel_response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, Request.STATUS_CANCELED)

        done_req = Request.objects.create(
            client_name="Done client",
            phone="+79000000009",
            address="Addr",
            problem_text="Done issue",
            status=Request.STATUS_DONE,
            assigned_to=self.master1,
        )
        self.client.post(reverse("cancel_request", kwargs={"request_id": done_req.id}))
        done_req.refresh_from_db()
        self.assertEqual(done_req.status, Request.STATUS_DONE)

    def test_master_take_race_returns_409_for_second_request(self):
        req = Request.objects.create(
            client_name="Client",
            phone="+79000000002",
            address="Addr",
            problem_text="Issue",
            status=Request.STATUS_ASSIGNED,
            assigned_to=self.master1,
        )
        self.client.force_login(self.master1)

        first = self.client.post(reverse("take_request", kwargs={"request_id": req.id}))
        second = self.client.post(reverse("take_request", kwargs={"request_id": req.id}))

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 409)
        req.refresh_from_db()
        self.assertEqual(req.status, Request.STATUS_IN_PROGRESS)

    def test_master_complete_only_from_in_progress(self):
        req = Request.objects.create(
            client_name="Client",
            phone="+79000000003",
            address="Addr",
            problem_text="Issue",
            status=Request.STATUS_ASSIGNED,
            assigned_to=self.master1,
        )
        self.client.force_login(self.master1)
        bad = self.client.post(reverse("complete_request", kwargs={"request_id": req.id}))
        self.assertEqual(bad.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, Request.STATUS_ASSIGNED)

        req.status = Request.STATUS_IN_PROGRESS
        req.save(update_fields=["status", "updated_at"])
        good = self.client.post(reverse("complete_request", kwargs={"request_id": req.id}))
        self.assertEqual(good.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, Request.STATUS_DONE)
