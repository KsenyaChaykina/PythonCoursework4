from django.core.management.base import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = CustomUser.objects.create(email="admin@admin.com")
        user.set_password("123qwe")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Создан админ с email {user.email}"))
