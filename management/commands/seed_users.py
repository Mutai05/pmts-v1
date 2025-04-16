from django.core.management.base import BaseCommand
from accounts.models import User
from departments.models import Department
from faker import Faker

class Command(BaseCommand):
    help = 'Seed user data'

    def handle(self, *args, **options):
        fake = Faker()
        
        # Ensure departments exist first
        departments = Department.objects.all()
        if not departments.exists():
            self.stdout.write(self.style.ERROR('No departments found. Please seed departments first.'))
            return

        # Create superuser
        if not User.objects.filter(email='admin@county.gov').exists():
            User.objects.create_superuser(
                email='admin@county.gov',
                password='admin123',
                first_name='County',
                last_name='Admin',
                role='executive'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin@county.gov'))

        # Create executive users
        executive_emails = [
            'governor@county.gov',
            'deputy@county.gov',
            'clerk@county.gov'
        ]
        for email in executive_emails:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='exec123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role='executive'
                )
                self.stdout.write(self.style.SUCCESS(f'Created executive user: {email}'))

        # Create departmental users
        for department in departments:
            email = f"head.{department.name.lower().replace(' ', '_')}@county.gov"
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='dept123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role='departmental',
                    department=department
                )
                self.stdout.write(self.style.SUCCESS(f'Created department head: {email}'))

        # Create public users
        for _ in range(5):  # Reduced from 20 for initial testing
            email = fake.unique.email()
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='public123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role='public'
                )
                self.stdout.write(self.style.SUCCESS(f'Created public user: {email}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded user data'))