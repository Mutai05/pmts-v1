from django.core.management.base import BaseCommand
from django.db import transaction
from departments.models import Department
from locations.models import County, SubCounty, Ward


class Command(BaseCommand):
    help = 'Populate initial seed data for Trans-Nzoia County PMTS'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate seed data...')

        with transaction.atomic():
            self._create_departments()
            self._create_locations()

        self.stdout.write(self.style.SUCCESS('Successfully populated seed data'))

    def _create_departments(self):
        """Create the county departments."""
        self.stdout.write('Creating departments...')
        departments = [
            {
                'name': 'Public Service Management & Governance',
                'description': 'Responsible for overseeing public service delivery and governance in the county.'
            },
            {
                'name': 'Water, Environment, Natural Resources & Climate Change',
                'description': 'Manages water resources, environmental conservation, and climate change initiatives.'
            },
            {
                'name': 'Lands, Housing, Physical Planning & Urban Development',
                'description': 'Handles land administration, housing development, and urban planning.'
            },
            {
                'name': 'Public Works, Roads, Transport Infrastructure & Energy',
                'description': 'Oversees infrastructure development including roads, transport, and energy.'
            },
            {
                'name': 'Health Services & Sanitation',
                'description': 'Responsible for healthcare services and sanitation programs across the county.'
            },
            {
                'name': 'Education & Technical Training',
                'description': 'Manages educational institutions and technical training programs.'
            },
            {
                'name': 'Finance & Economic Planning',
                'description': 'Handles county finances, budgeting, and economic development planning.'
            },
            {
                'name': 'Agriculture, Irrigation, Livestock, Fisheries & Cooperative Development',
                'description': 'Supports agricultural activities, irrigation projects, and cooperative societies.'
            },
            {
                'name': 'Trade & Industrialization',
                'description': 'Promotes trade, industrialization, and business development.'
            },
            {
                'name': 'Gender, Youth, Sports, Culture & Tourism',
                'description': 'Focuses on gender equality, youth empowerment, sports, cultural preservation, and tourism.'
            }
        ]

        for dept_data in departments:
            Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(departments)} departments'))

    def _create_locations(self):
        """Create the county, sub-counties, and wards."""
        self.stdout.write('Creating locations...')

        # Create Trans-Nzoia County
        county, _ = County.objects.get_or_create(
            name='Trans-Nzoia',
            defaults={'code': 'TNZ'}
        )

        # Sub-counties and their wards
        locations = {
            'Kwanza': ['Kwanza', 'Keiyo', 'Bidii', 'Kapomboi'],
            'Endebess': ['Endebess', 'Matumbei', 'Chepchoina'],
            'Saboti': ['Kinyoro', 'Matisi', 'Tuwan', 'Saboti', 'Machewa'],
            'Kiminini': ['Kiminini', 'Waitaluk', 'Sirende', 'Hospital', 'Sikhendu', 'Nabiswa'],
            'Cherang\'any': ['Motosiet', 'Sitatunga', 'Kaplamai', 'Makutano', 'Sinyereri',
                          'Cherang\'any-Suwerwa', 'Chepsiro-Kiptoror']
        }

        # Create sub-counties and wards
        total_wards = 0
        for subcounty_name, wards in locations.items():
            subcounty, _ = SubCounty.objects.get_or_create(
                name=subcounty_name,
                county=county
            )

            for ward_name in wards:
                Ward.objects.get_or_create(
                    name=ward_name,
                    subcounty=subcounty
                )
                total_wards += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created 1 county, {len(locations)} sub-counties, and {total_wards} wards'
        ))