from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from dashboard.models import Department, SubCounty, Ward, Project, ProjectPhoto, Feedback, Notification, ActivityLog
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed the database with realistic Trans Nzoia PMTS data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting seeding process...")

        # Clear existing data
        self.stdout.write("Clearing existing data...")
        User.objects.exclude(is_superuser=True).delete()
        Department.objects.all().delete()
        SubCounty.objects.all().delete()
        Ward.objects.all().delete()
        Project.objects.all().delete()
        ProjectPhoto.objects.all().delete()
        Feedback.objects.all().delete()
        Notification.objects.all().delete()
        ActivityLog.objects.all().delete()

        # Create users
        self.stdout.write("Creating users...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@pmts.go.ke'
            )
        user1, _ = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@pmts.go.ke',
                'is_active': True
            }
        )
        user1.set_password('test123')
        user1.save()

        # Create departments
        self.stdout.write("Creating departments...")
        departments = [
            {"name": "Public Works & Transport", "icon_class": "bi-truck"},
            {"name": "Education & Training", "icon_class": "bi-book"},
            {"name": "Health Services", "icon_class": "bi-hospital"},
            {"name": "Water & Environment", "icon_class": "bi-droplet"},
            {"name": "Agriculture & Livestock", "icon_class": "bi-tree"},
            {"name": "Trade & Industry", "icon_class": "bi-shop"},
            {"name": "Finance & Planning", "icon_class": "bi-calculator"},
            {"name": "Youth & Sports", "icon_class": "bi-trophy"},
            {"name": "Public Service Management", "icon_class": "bi-person"},
        ]
        dept_objs = [Department.objects.create(**dept) for dept in departments]

        # Create sub-counties
        self.stdout.write("Creating sub-counties...")
        subcounties = [
            {"name": "Kwanza"},
            {"name": "Endebess"},
            {"name": "Saboti"},
            {"name": "Kiminini"},
            {"name": "Cherangany"},
        ]
        sc_objs = [SubCounty.objects.create(**sc) for sc in subcounties]

        # Create wards
        self.stdout.write("Creating wards...")
        wards = [
            # Kwanza
            {"name": "Kaplamai", "sub_county": sc_objs[0]},
            {"name": "Kwanza", "sub_county": sc_objs[0]},
            {"name": "Keiyo", "sub_county": sc_objs[0]},
            {"name": "Kaisagat", "sub_county": sc_objs[0]},
            # Endebess
            {"name": "Motiosiot", "sub_county": sc_objs[1]},
            {"name": "Endebess", "sub_county": sc_objs[1]},
            {"name": "Chepchoina", "sub_county": sc_objs[1]},
            # Saboti
            {"name": "Sinyerere", "sub_county": sc_objs[2]},
            {"name": "Kinyoro", "sub_county": sc_objs[2]},
            {"name": "Machewa", "sub_county": sc_objs[2]},
            {"name": "Saboti", "sub_county": sc_objs[2]},
            # Kiminini
            {"name": "Kiminini", "sub_county": sc_objs[3]},
            {"name": "Waitaluk", "sub_county": sc_objs[3]},
            {"name": "Sikhendu", "sub_county": sc_objs[3]},
            # Cherangany
            {"name": "Sitatunga", "sub_county": sc_objs[4]},
            {"name": "Cherangany", "sub_county": sc_objs[4]},
            {"name": "Makutano", "sub_county": sc_objs[4]},
        ]
        ward_objs = [Ward.objects.create(**ward) for ward in wards]

        # Create projects
        self.stdout.write("Creating projects...")
        projects = [
            {
                "name": "Kitale-Turbo Road Upgrade",
                "department": dept_objs[0],  # Public Works
                "sub_county": sc_objs[0],   # Kwanza
                "ward": ward_objs[0],       # Kaplamai
                "status": "Completed",
                "budget_allocation": Decimal("15000000.00"),
                "expenditure": Decimal("14500000.00"),
                "completion_percentage": 100,
                "map_link": "https://maps.example.com/pin1",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "County Roads Board",
                "remarks": "Completed ahead of schedule",
                "contractor": "TransBuild Ltd",
                "location": "Near Kitale Town",
                "financial_year": "2024-2025",
                "source_of_funds": "County Government",
                "description": "Upgrading 10km of gravel road to bitumen standard",
            },
            {
                "name": "Endebess Primary Renovation",
                "department": dept_objs[1],  # Education
                "sub_county": sc_objs[1],   # Endebess
                "ward": ward_objs[4],       # Motiosiot
                "status": "Ongoing",
                "budget_allocation": Decimal("5000000.00"),
                "expenditure": Decimal("3000000.00"),
                "completion_percentage": 60,
                "map_link": "https://maps.example.com/pin2",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "Education Department",
                "remarks": "Ongoing, needs more funds",
                "contractor": "EduConstruct",
                "location": "Endebess Town",
                "financial_year": "2024-2025",
                "source_of_funds": "NG-CDF",
                "description": "Renovating classrooms and adding new facilities",
            },
            {
                "name": "Saboti Borehole Installation",
                "department": dept_objs[3],  # Water
                "sub_county": sc_objs[2],   # Saboti
                "ward": ward_objs[7],       # Sinyerere
                "status": "Stalled",
                "budget_allocation": Decimal("8000000.00"),
                "expenditure": Decimal("1000000.00"),
                "completion_percentage": 20,
                "map_link": "https://maps.example.com/pin3",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "N/A",
                "remarks": "Stalled due to funding issues",
                "contractor": "N/A",
                "location": "Sinyerere Village",
                "financial_year": "2023-2024",
                "source_of_funds": "N/A",
                "description": "Drilling borehole for community water supply",
            },
            {
                "name": "Kiminini Health Centre Expansion",
                "department": dept_objs[2],  # Health
                "sub_county": sc_objs[3],   # Kiminini
                "ward": ward_objs[11],      # Kiminini
                "status": "Ongoing",
                "budget_allocation": Decimal("12000000.00"),
                "expenditure": Decimal("9000000.00"),
                "completion_percentage": 75,
                "map_link": "https://maps.example.com/pin4",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "Health Department",
                "remarks": "On track",
                "contractor": "HealthBuild Ltd",
                "location": "Kiminini Town",
                "financial_year": "2024-2025",
                "source_of_funds": "County Government",
                "description": "Expanding maternity wing and adding labs",
            },
            {
                "name": "Cherangany Irrigation Project",
                "department": dept_objs[4],  # Agriculture
                "sub_county": sc_objs[4],   # Cherangany
                "ward": ward_objs[14],      # Sitatunga
                "status": "Completed",
                "budget_allocation": Decimal("20000000.00"),
                "expenditure": Decimal("20000000.00"),
                "completion_percentage": 100,
                "map_link": "https://maps.example.com/pin5",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "Agriculture Board",
                "remarks": "Fully operational",
                "contractor": "AgriTech Ltd",
                "location": "Sitatunga Plains",
                "financial_year": "2024-2025",
                "source_of_funds": "National Government",
                "description": "Installing irrigation for 50 hectares of farmland",
            },
            {
                "name": "Kwanza Market Stalls",
                "department": dept_objs[5],  # Trade
                "sub_county": sc_objs[0],   # Kwanza
                "ward": ward_objs[1],       # Kwanza
                "status": "Ongoing",
                "budget_allocation": Decimal("3000000.00"),
                "expenditure": Decimal("1500000.00"),
                "completion_percentage": 50,
                "map_link": "https://maps.example.com/pin6",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "Trade Department",
                "remarks": "Phase 1 complete",
                "contractor": "N/A",
                "location": "Kwanza Market",
                "financial_year": "2024-2025",
                "source_of_funds": "County Government",
                "description": "Building 20 market stalls for traders",
            },
            {
                "name": "Saboti Youth Centre",
                "department": dept_objs[7],  # Youth
                "sub_county": sc_objs[2],   # Saboti
                "ward": ward_objs[10],      # Saboti
                "status": "Stalled",
                "budget_allocation": Decimal("6000000.00"),
                "expenditure": Decimal("500000.00"),
                "completion_percentage": 10,
                "map_link": "",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "N/A",
                "remarks": "Awaiting funds",
                "contractor": "N/A",
                "location": "Saboti Town",
                "financial_year": "2023-2024",
                "source_of_funds": "N/A",
                "description": "Constructing youth centre with sports facilities",
            },
            {
                "name": "Endebess ECDE Classroom",
                "department": dept_objs[1],  # Education
                "sub_county": sc_objs[1],   # Endebess
                "ward": ward_objs[5],       # Endebess
                "status": "Completed",
                "budget_allocation": Decimal("4000000.00"),
                "expenditure": Decimal("4000000.00"),
                "completion_percentage": 100,
                "map_link": "https://maps.example.com/pin7",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "Education Department",
                "remarks": "Fully functional",
                "contractor": "EduConstruct",
                "location": "Endebess Village",
                "financial_year": "2024-2025",
                "source_of_funds": "NG-CDF",
                "description": "Building 2 ECDE classrooms",
            },
            {
                "name": "Kiminini Water Pipeline",
                "department": dept_objs[3],  # Water
                "sub_county": sc_objs[3],   # Kiminini
                "ward": ward_objs[12],      # Waitaluk
                "status": "Ongoing",
                "budget_allocation": Decimal("10000000.00"),
                "expenditure": Decimal("7000000.00"),
                "completion_percentage": 70,
                "map_link": "https://maps.example.com/pin8",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "Water Department",
                "remarks": "Pipe laying in progress",
                "contractor": "AquaTech Ltd",
                "location": "Waitaluk Area",
                "financial_year": "2024-2025",
                "source_of_funds": "County Government",
                "description": "Installing 5km water pipeline",
            },
            {
                "name": "Cherangany Sports Field",
                "department": dept_objs[7],  # Youth
                "sub_county": sc_objs[4],   # Cherangany
                "ward": ward_objs[15],      # Cherangany
                "status": "Ongoing",
                "budget_allocation": Decimal("7000000.00"),
                "expenditure": Decimal("4000000.00"),
                "completion_percentage": 55,
                "map_link": "https://maps.example.com/pin9",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "Youth Department",
                "remarks": "Ground leveling done",
                "contractor": "SportBuild Ltd",
                "location": "Cherangany Town",
                "financial_year": "2024-2025",
                "source_of_funds": "NG-CDF",
                "description": "Developing sports field with track",
            },
            {
                "name": "Kwanza Dispensary Upgrade",
                "department": dept_objs[2],  # Health
                "sub_county": sc_objs[0],   # Kwanza
                "ward": ward_objs[2],       # Keiyo
                "status": "Completed",
                "budget_allocation": Decimal("8000000.00"),
                "expenditure": Decimal("8000000.00"),
                "completion_percentage": 100,
                "map_link": "https://maps.example.com/pin10",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "Health Department",
                "remarks": "Operational",
                "contractor": "HealthBuild Ltd",
                "location": "Keiyo Village",
                "financial_year": "2024-2025",
                "source_of_funds": "County Government",
                "description": "Upgrading dispensary with new wards",
            },
            {
                "name": "Saboti Bridge Construction",
                "department": dept_objs[0],  # Public Works
                "sub_county": sc_objs[2],   # Saboti
                "ward": ward_objs[8],       # Kinyoro
                "status": "Stalled",
                "budget_allocation": Decimal("25000000.00"),
                "expenditure": Decimal("5000000.00"),
                "completion_percentage": 30,
                "map_link": "",
                "created_at": timezone.datetime(2025, 1, 1),
                "updated_at": timezone.datetime(2025, 1, 1),
                "implementing_agency": "N/A",
                "remarks": "Delayed due to contractor issues",
                "contractor": "N/A",
                "location": "Kinyoro River",
                "financial_year": "2023-2024",
                "source_of_funds": "N/A",
                "description": "Constructing 50m bridge",
            },
        ]
        project_objs = []
        for proj in projects:
            project = Project.objects.create(**proj)
            project_objs.append(project)
            # Add photos for some projects
            if proj["name"] in [
                "Kitale-Turbo Road Upgrade",
                "Endebess Primary Renovation",
                "Kiminini Health Centre Expansion",
                "Cherangany Irrigation Project",
                "Endebess ECDE Classroom",
                "Kwanza Dispensary Upgrade"
            ]:
                ProjectPhoto.objects.create(
                    project=project,
                    image=f"project_photos/{proj['name'].lower().replace(' ', '_')}.jpg",
                    caption=f"Photo of {proj['name']}"
                )

        # Create feedback
        self.stdout.write("Creating feedback...")
        feedbacks = [
            {"project": project_objs[0], "rating": 5, "comment": "Excellent road quality!"},
            {"project": project_objs[0], "rating": 4, "comment": "Completed on time."},
            {"project": project_objs[1], "rating": 3, "comment": "Good progress, needs faster work."},
            {"project": project_objs[2], "rating": 2, "comment": "Project stalled, needs attention."},
            {"project": project_objs[3], "rating": 4, "comment": "Health centre looking good!"},
            {"project": project_objs[4], "rating": 5, "comment": "Great for farmers!"},
            {"project": project_objs[7], "rating": 5, "comment": "Perfect for kids!"},
            {"project": project_objs[9], "rating": 3, "comment": "Sports field needs more work."},
        ]
        for fb in feedbacks:
            Feedback.objects.create(**fb)

        # Create notifications
        self.stdout.write("Creating notifications...")
        notifications = [
            {"user": user1, "title": "Project Completed", "message": "Kitale-Turbo Road Upgrade is complete!", "type": "info"},
            {"user": user1, "title": "Feedback Received", "message": "New feedback on Endebess Primary Renovation.", "type": "info"},
            {"user": user1, "title": "Project Stalled", "message": "Saboti Borehole Installation has stalled.", "type": "alert"},
            {"user": user1, "title": "Budget Update", "message": "Kiminini Health Centre budget updated.", "type": "info"},
            {"user": user1, "title": "New Project", "message": "Cherangany Irrigation Project started.", "type": "info"},
        ]
        for notif in notifications:
            Notification.objects.create(**notif)

        # Create activity logs
        self.stdout.write("Creating activity logs...")
        activity_logs = [
            {"user": user1, "project": project_objs[0], "type": "status", "message": "Kitale-Turbo Road marked as Completed."},
            {"user": user1, "project": project_objs[1], "type": "update", "message": "Endebess Primary Renovation updated to 60%."},
            {"user": user1, "project": project_objs[2], "type": "status", "message": "Saboti Borehole changed to Stalled."},
            {"user": user1, "project": project_objs[3], "type": "feedback", "message": "Feedback submitted for Kiminini Health Centre."},
            {"user": user1, "project": project_objs[4], "type": "status", "message": "Cherangany Irrigation marked as Completed."},
            {"user": user1, "project": project_objs[7], "type": "status", "message": "Endebess ECDE Classroom marked as Completed."},
            {"user": user1, "project": project_objs[9], "type": "update", "message": "Cherangany Sports Field updated to 55%."},
            {"user": user1, "project": project_objs[11], "type": "status", "message": "Saboti Bridge changed to Stalled."},
        ]
        for log in activity_logs:
            ActivityLog.objects.create(**log)

        # Summary
        self.stdout.write(self.style.SUCCESS("\nSeeding complete!"))
        self.stdout.write(f"Users: {User.objects.count()}")
        self.stdout.write(f"Departments: {Department.objects.count()}")
        self.stdout.write(f"Sub-Counties: {SubCounty.objects.count()}")
        self.stdout.write(f"Wards: {Ward.objects.count()}")
        self.stdout.write(f"Projects: {Project.objects.count()}")
        self.stdout.write(f"Project Photos: {ProjectPhoto.objects.count()}")
        self.stdout.write(f"Feedback: {Feedback.objects.count()}")
        self.stdout.write(f"Notifications: {Notification.objects.count()}")
        self.stdout.write(f"Activity Logs: {ActivityLog.objects.count()}")
        self.stdout.write("\nSample Projects:")
        for p in Project.objects.all()[:3]:
            self.stdout.write(f"- {p.name}: {p.status}, {p.completion_percentage}%")