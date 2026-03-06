from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from requests_app.models import Request
from requests_app.services import create_request


class Command(BaseCommand):
    help = "Seed initial data: dispatcher, masters and sample requests."

    def handle(self, *args, **options):
        dispatcher_group, _ = Group.objects.get_or_create(name="dispatcher")
        master_group, _ = Group.objects.get_or_create(name="master")

        dispatcher, _ = User.objects.get_or_create(username="dispatcher1", defaults={"is_staff": True})
        dispatcher.set_password("dispatcher123")
        dispatcher.save()
        dispatcher.groups.add(dispatcher_group)

        master1, _ = User.objects.get_or_create(username="master1")
        master1.set_password("master123")
        master1.save()
        master1.groups.add(master_group)

        master2, _ = User.objects.get_or_create(username="master2")
        master2.set_password("master123")
        master2.save()
        master2.groups.add(master_group)

        if Request.objects.count() == 0:
            r1 = create_request(
                client_name="Иван Петров",
                phone="+79000000001",
                address="ул. Ленина, 1",
                problem_text="Не работает розетка",
                actor=dispatcher,
            )
            r2 = create_request(
                client_name="Анна Смирнова",
                phone="+79000000002",
                address="ул. Гагарина, 12",
                problem_text="Течет кран",
                actor=dispatcher,
            )
            r3 = create_request(
                client_name="Олег Сидоров",
                phone="+79000000003",
                address="пр. Мира, 5",
                problem_text="Сломалась ручка двери",
                actor=dispatcher,
            )

            r1.status = Request.STATUS_ASSIGNED
            r1.assigned_to = master1
            r1.save(update_fields=["status", "assigned_to", "updated_at"])

            r2.status = Request.STATUS_IN_PROGRESS
            r2.assigned_to = master2
            r2.save(update_fields=["status", "assigned_to", "updated_at"])

            r3.status = Request.STATUS_DONE
            r3.assigned_to = master1
            r3.save(update_fields=["status", "assigned_to", "updated_at"])

            create_request(
                client_name="Мария Иванова",
                phone="+79000000004",
                address="ул. Центральная, 7",
                problem_text="Замена лампы в подъезде",
                actor=dispatcher,
            )

        self.stdout.write(self.style.SUCCESS("Seed data created/updated successfully."))
