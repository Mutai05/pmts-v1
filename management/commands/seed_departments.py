from django.core.management.base import BaseCommand
from departments.models import Department
from faker import Faker

class Command(BaseCommand):
    help = 'Seed department data'

    def handle(self, *args, **options):
        fake = Faker()
        
        # List of common county government departments
        department_names = [
            "Agriculture, Livestock and Fisheries",
            "Education and Vocational Training",
            "Health Services",
            "Finance and Economic Planning",
            "Lands, Housing and Physical Planning",
            "Water, Environment and Natural Resources",
            "Transport, Infrastructure and Public Works",
            "Trade, Tourism and Cooperatives",
            "Youth, Sports and Culture",
            "Public Service and Administration",
            "ICT and E-Government",
            "Gender, Children and Social Services",
            "Industrialization and Enterprise Development",
            "Energy and Petroleum",
            "Urban Development and Planning",
        ]

        # Create departments
        created_count = 0
        for name in department_names:
            # Check if department already exists
            if not Department.objects.filter(name=name).exists():
                Department.objects.create(
                    name=name,
                    description=fake.paragraph(nb_sentences=3)
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} departments'))

        # If all departments already existed
        if created_count == 0:
            self.stdout.write(self.style.WARNING('All departments already exist in the database'))