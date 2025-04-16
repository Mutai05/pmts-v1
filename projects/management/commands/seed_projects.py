import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project, ProjectProgress, ProjectPhoto, ProjectFeedback, StaffReply
from departments.models import Department
from locations.models import Ward
from django.utils.text import slugify
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with over 200 varied demo projects'

    def add_arguments(self, parser):
        parser.add_argument('--projects', type=int, default=200, help='Number of projects to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing projects before creating new ones')

    def handle(self, *args, **options):
        num_projects = options['projects']
        clear_existing = options['clear']

        if clear_existing:
            self.stdout.write(self.style.WARNING('Clearing existing project data (Projects, Progress, Photos, Feedback, Replies)...'))
            StaffReply.objects.all().delete()
            ProjectFeedback.objects.all().delete()
            ProjectProgress.objects.all().delete()
            ProjectPhoto.objects.all().delete()
            Project.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing project data cleared.'))

        # Check for necessary data
        departments = list(Department.objects.all())
        if not departments:
            self.stdout.write(self.style.ERROR('No departments found. Please seed departments first.'))
            return

        wards = list(Ward.objects.all())
        if not wards:
            self.stdout.write(self.style.ERROR('No wards found. Please seed locations first.'))
            return

        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create a superuser first.'))
            return

        # --- Create Department Users --- #
        self.stdout.write(self.style.WARNING('Creating/Verifying Department Users...'))
        department_users = []
        password = "password123"
        for dept in departments:
            dept_name_slug = slugify(dept.name)
            email = f"{dept_name_slug}@department.example.com"
            try:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'email': email,
                        'first_name': dept.name,
                        'last_name': 'User',
                        'department': dept,
                        'role': 'editor'
                    }
                )
                if created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Created user: {email} for {dept.name}'))
                else:
                    if user.department != dept or user.role != 'editor':
                        user.department = dept
                        user.role = 'editor'
                        user.save()
                        self.stdout.write(self.style.NOTICE(f'Updated existing user: {email}'))
                    else:
                        self.stdout.write(self.style.NOTICE(f'User {email} already exists.'))
                department_users.append(user)
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {email} ({email}): {e}'))
            except AttributeError as e:
                self.stdout.write(self.style.ERROR(f'Error setting attributes for user {email}. Does User model have "department" and "role" fields? Error: {e}'))
                return
        self.stdout.write(self.style.SUCCESS(f'Finished creating/verifying {len(department_users)} department users.'))
        staff_users = [admin_user] + department_users

        # Prepare data lists for random selection
        project_prefixes = [
            "Construction of", "Renovation of", "Expansion of", "Rehabilitation of",
            "Modernization of", "Building", "Development of", "Upgrading",
            "Establishment of", "Improvement of", "Installation of", "Revitalization of"
        ]

        project_types = [
            "Market", "Road", "Bridge", "Hospital", "School", "Health Center", "Dispensary",
            "Water Project", "Borehole", "Community Hall", "Stadium", "Irrigation Scheme",
            "Drainage System", "Social Hall", "ECDE Center", "Youth Polytechnic", "Bus Park",
            "ICT Hub", "Library", "Offices", "Storage Facility", "Milk Cooling Plant",
            "Fish Pond", "Green House", "Resource Center", "Footbridge", "Livestock Market"
        ]

        project_locations = [
            "in", "at", "near", "around", "along", "within", "connecting"
        ]

        financial_years = ["2021-2022", "2022-2023", "2023-2024", "2024-2025"]

        implementing_agencies = [
            "Trans-Nzoia County Government", "Ministry of Roads", "Ministry of Education",
            "Ministry of Health", "Water Services Board", "Rural Electrification Authority",
            "KPLC", "Kenya Rural Roads Authority", "Kenya Urban Roads Authority",
            "County Department of Public Works", "County Department of Infrastructure",
            "Trans-Nzoia Water Company", "National Irrigation Board"
        ]

        contractors = [
            "Simba Contractors Ltd", "Mwanainchi Builders", "Pioneer Construction Co.",
            "Alpha Developers", "Modern Constructors Ltd", "County Builders Ltd",
            "Reliable Contractors", "Equity Construction", "Upward Developers",
            "Jijenge Contractors", "Mafundi Solutions Ltd", "Jenga Better Co.",
            "Unity Developers", "Landmark Builders", "Strategic Construction Ltd",
            "Premier Contractors", "Ujuzi Construction", "Imara Builders", "Safiri Roads Ltd",
            None
        ]

        challenges_templates = [
            "Delayed funding disbursement affecting timeline.",
            "Heavy rainfall causing delays in construction.",
            "Community disputes over project placement.",
            "Material price fluctuations affecting budget.",
            "Contractor capacity issues slowing progress.",
            "Land acquisition delays affecting project start.",
            "Inadequate skilled labor in the local area.",
            "Supply chain disruptions for critical materials.",
            "Access challenges due to poor road infrastructure.",
            "Stakeholder coordination complications.",
            "Regulatory approval delays.",
            "",
        ]

        status_weights = {
            'completed': 0.3,
            'ongoing': 0.4,
            'stalled': 0.1,
            'not_started': 0.1,
            'under_procurement': 0.1
        }

        progress_descriptions = [
            "Foundation work completed.",
            "Structural framework in progress.",
            "Roofing phase complete.",
            "Interior finishes being installed.",
            "Electrical wiring and plumbing installation in progress.",
            "External works (landscaping, access roads) ongoing.",
            "Quality assurance and testing phase.",
            "Final touches and cleanup in progress.",
            "Project documentation and handover preparation.",
            "Community engagement and training ongoing."
        ]

        description_templates = [
            "This project aims to {action} {facility} for the residents of {location}. It will improve {benefit} and contribute to {outcome}.",
            "The {facility} project in {location} will enhance {benefit} for local communities. Key components include {components}.",
            "A critical infrastructure development project to {action} {facility} in {location}, addressing the challenges of {challenges} while promoting {outcome}.",
            "This initiative involves the {action} of a modern {facility} that will serve {population} residents of {location} and surrounding areas. The project focuses on {components}.",
            "An essential development initiative to {action} {facility} in {location}, designed to improve {benefit} and enhance quality of life for local communities."
        ]

        actions = [
            "construct", "develop", "establish", "build", "renovate", "upgrade", "modernize", "expand", "rehabilitate"
        ]

        benefits = [
            "access to essential services", "public health", "education standards", "water supply",
            "transportation efficiency", "market access for farmers", "community cohesion",
            "youth development", "economic opportunities", "food security", "public safety",
            "waste management", "environmental conservation", "energy access", "digital connectivity"
        ]

        outcomes = [
            "sustainable development", "poverty reduction", "improved livelihoods", "economic growth",
            "better health outcomes", "enhanced education performance", "increased agricultural productivity",
            "reduced transportation costs", "improved public service delivery", "community empowerment",
            "gender equality", "climate resilience", "disaster preparedness", "social inclusion"
        ]

        components = [
            "modern facilities, equipment, and trained personnel",
            "sustainable design features, community engagement spaces, and essential services",
            "improved infrastructure, capacity building, and management systems",
            "technology integration, accessibility features, and environmental considerations",
            "community participation mechanisms, monitoring systems, and maintenance protocols",
            "renewable energy solutions, water conservation measures, and waste management systems",
            "inclusive design elements, technological innovations, and operational efficiency measures"
        ]

        populations = [
            "over 5,000", "approximately 10,000", "more than 15,000", "around 8,000",
            "an estimated 12,000", "nearly 20,000", "about 7,500", "roughly 25,000"
        ]

        # Begin creating projects
        created_count = 0
        self.stdout.write(self.style.WARNING(f'Creating {num_projects} projects...'))

        for i in range(1, num_projects + 1):
            # Select random data for this project
            department = random.choice(departments)
            ward = random.choice(wards)

            # Generate a realistic project name
            prefix = random.choice(project_prefixes)
            project_type = random.choice(project_types)
            location_prep = random.choice(project_locations)
            project_name = f"{prefix} {project_type} {location_prep} {ward.name}"

            # Ensure unique slug
            base_slug = slugify(project_name)
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Generate description
            template = random.choice(description_templates)
            description = template.format(
                action=random.choice(actions),
                facility=project_type.lower(),
                location=ward.name,
                benefit=random.choice(benefits),
                outcome=random.choice(outcomes),
                components=random.choice(components),
                population=random.choice(populations),
                challenges=random.choice(benefits)
            )

            # Financial year
            financial_year = random.choice(financial_years)

            # Determine status based on weights
            status = random.choices(
                list(status_weights.keys()),
                weights=list(status_weights.values()),
                k=1
            )[0]

            # Set realistic dates based on financial year and status
            year_start = int(financial_year.split('-')[0])

            # Start date within the financial year
            start_date_earliest = date(year_start, 7, 1)
            start_date_latest = date(year_start + 1, 6, 30)
            days_in_fy = (start_date_latest - start_date_earliest).days

            # Random start date within financial year
            start_date = start_date_earliest + timedelta(days=random.randint(0, days_in_fy))

            # End date logic based on status
            if status == 'completed':
                min_duration = 30
                max_duration = 365
                end_date = start_date + timedelta(days=random.randint(min_duration, max_duration))
                percentage_complete = 100
            elif status == 'ongoing':
                min_duration = 180
                max_duration = 365 * 2
                end_date = start_date + timedelta(days=random.randint(min_duration, max_duration))
                percentage_complete = random.randint(25, 90)
            elif status == 'stalled':
                min_duration = 180
                max_duration = 365 * 3
                end_date = start_date + timedelta(days=random.randint(min_duration, max_duration))
                percentage_complete = random.randint(10, 50)
            elif status == 'not_started':
                min_duration = 180
                max_duration = 365 * 2
                end_date = date.today() + timedelta(days=random.randint(min_duration, max_duration))
                percentage_complete = 0
            else:
                min_duration = 365
                max_duration = 365 * 2
                end_date = date.today() + timedelta(days=random.randint(min_duration, max_duration))
                percentage_complete = 0

            # Budget allocation (vary by project type)
            if "Road" in project_type or "Bridge" in project_type:
                min_budget = 5000000
                max_budget = 50000000
            elif "Hospital" in project_type:
                min_budget = 10000000
                max_budget = 100000000
            elif "School" in project_type or "Center" in project_type:
                min_budget = 3000000
                max_budget = 20000000
            elif "Water" in project_type or "Borehole" in project_type:
                min_budget = 1000000
                max_budget = 10000000
            else:
                min_budget = 500000
                max_budget = 15000000

            budget_allocation = Decimal(random.randint(min_budget, max_budget))

            # Expenditure based on percentage complete - Fix the type error by converting to Decimal
            expenditure = budget_allocation * (Decimal(percentage_complete) / Decimal('100'))

            # Randomly choose other fields
            funding_source = random.choice(['county', 'national', 'donor'])
            contractor = random.choice(contractors)
            implementing_agency = random.choice(implementing_agencies)
            challenges = random.choice(challenges_templates)

            # Create the project
            try:
                project = Project.objects.create(
                    name=project_name,
                    slug=slug,
                    description=description,
                    department=department,
                    ward=ward,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    percentage_complete=percentage_complete,
                    budget_allocation=budget_allocation,
                    expenditure=expenditure,
                    funding_source=funding_source,
                    contractor_name=contractor,
                    implementing_agency=implementing_agency,
                    financial_year=financial_year,
                    challenges=challenges,
                    # created_by=admin_user
                )
                created_count += 1

                # --- Add Random Progress Updates --- #
                if status in ['ongoing', 'completed', 'stalled'] and percentage_complete > 0:
                    num_updates = random.randint(1, 5)
                    current_progress_date = start_date + timedelta(days=random.randint(7, 30))
                    current_percentage = 0
                    for _ in range(num_updates):
                        if current_progress_date >= date.today() or current_percentage >= percentage_complete:
                            break

                        # Calculate the upper bound for the random increase, ensuring it's at least 5
                        upper_increase_limit = int((percentage_complete - current_percentage) / (num_updates - _ + 1)) if num_updates > _ else 20
                        random_increase_upper = max(5, upper_increase_limit) # Ensure upper bound >= 5
                        percentage_increase = random.randint(5, random_increase_upper)

                        update_percentage = min(percentage_complete, current_percentage + percentage_increase)

                        if update_percentage <= current_percentage:
                            update_percentage = min(percentage_complete, current_percentage + 5)

                        ProjectProgress.objects.create(
                            project=project,
                            date=current_progress_date,
                            percentage=update_percentage,
                            description=random.choice(progress_descriptions),
                            updated_by=random.choice(staff_users)
                        )
                        current_percentage = update_percentage
                        current_progress_date += timedelta(days=random.randint(15, 60))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create project {i}: {project_name}. Error: {e}'))

            # Print progress
            if created_count % 50 == 0:
                self.stdout.write(f'{created_count} projects created...')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} projects.'))

        # --- Seed Feedback, Flags, and Replies --- #
        projects_for_feedback = list(Project.objects.all())
        if not projects_for_feedback:
            self.stdout.write(self.style.WARNING('No projects available to add feedback to.'))
            return

        num_feedback = created_count * 3
        self.stdout.write(self.style.WARNING(f'Creating {num_feedback} feedback entries...'))

        fake_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Ken", "Liam", "Mia", "Noah", "Olivia"]
        fake_domains = ["mail.com", "web.com", "internet.org", "email.net"]
        feedback_comments = [
            "Excellent progress, keep up the good work!",
            "Concerned about the delays, hope it finishes soon.",
            "The quality of work seems subpar.",
            "Very happy with this project in our area.",
            "Need more frequent updates on the status.",
            "Is the budget being used effectively?",
            "This project has significantly improved our community.",
            "The contractor is doing a fantastic job.",
            "Communication regarding this project needs improvement.",
            "When will the final phase be completed?",
            "Looks promising, eagerly waiting for completion.",
            "The environmental impact needs more consideration.",
            "Good value for taxpayer money.",
            "Project seems stalled, what's happening?",
            "Appreciate the transparency on this portal.",
            "This is exactly what our ward needed."
        ]
        reply_texts = [
            "Thank you for your feedback! We appreciate your support.",
            "We acknowledge the delays and are working to expedite the process.",
            "Thank you for raising quality concerns. We will investigate with the contractor.",
            "We are glad the project is having a positive impact.",
            "Noted. We will strive to provide more regular updates.",
            "Budget utilization is being monitored closely. Details are on the project page.",
            "Thank you! We aim to deliver impactful projects.",
            "We will pass on your compliments to the contractor.",
            "Thank you for the feedback on communication. We will work on improving it.",
            "The expected completion date is [Date]. We will update if this changes.",
            "Thank you for your patience. We are working hard to complete it.",
            "Environmental impact assessments were conducted. We are adhering to regulations.",
            "We strive for responsible use of public funds. Thank you.",
            "Apologies for the lack of recent updates. We are addressing the issues causing the stall.",
            "Transparency is important to us. Thank you for using the portal.",
            "We are happy to hear the project meets the community's needs."
        ]

        created_feedback_ids = []
        feedback_count = 0
        for _ in range(num_feedback):
            try:
                project = random.choice(projects_for_feedback)
                ward = random.choice(wards) # Random location, not tied to project for variety

                # --- Ensure the selected ward has a subcounty --- #
                if not ward.subcounty:
                    # Skip this iteration if the randomly chosen ward doesn't have a subcounty
                    # self.stdout.write(self.style.NOTICE(f'Skipping feedback for ward {ward.name} as it has no subcounty.'))
                    continue
                # --- End Check --- #

                name = random.choice(fake_names) + " " + random.choice(["M.", "K.", "W."])
                email = name.split()[0].lower() + f"{random.randint(1,99)}@" + random.choice(fake_domains)

                feedback = ProjectFeedback.objects.create(
                    project=project,
                    name=name,
                    email=email,
                    ward=ward,
                    sub_county=ward.subcounty, # Now we know ward.subcounty is not null
                    rating=random.randint(1, 5),
                    comment=random.choice(feedback_comments)
                )
                created_feedback_ids.append(feedback.id)
                feedback_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create feedback entry. Error: {e}'))

            if feedback_count % 100 == 0:
                self.stdout.write(f'{feedback_count} feedback entries created...')
        self.stdout.write(self.style.SUCCESS(f'Successfully created {feedback_count} feedback entries.'))

        # --- Flag some feedback --- #
        if created_feedback_ids:
            num_to_flag = int(len(created_feedback_ids) * 0.15)
            ids_to_flag = random.sample(created_feedback_ids, k=min(num_to_flag, len(created_feedback_ids)))
            self.stdout.write(self.style.WARNING(f'Flagging {len(ids_to_flag)} feedback entries...'))
            updated_count = ProjectFeedback.objects.filter(id__in=ids_to_flag).update(flagged_inappropriate=True)
            self.stdout.write(self.style.SUCCESS(f'Flagged {updated_count} entries.'))

            reply_eligible_ids = list(set(created_feedback_ids) - set(ids_to_flag))
        else:
            reply_eligible_ids = []

        # --- Add Staff Replies --- #
        if reply_eligible_ids and staff_users:
            num_to_reply = int(len(reply_eligible_ids) * 0.3)
            ids_to_reply_to = random.sample(reply_eligible_ids, k=min(num_to_reply, len(reply_eligible_ids)))
            feedback_to_reply = ProjectFeedback.objects.filter(id__in=ids_to_reply_to)
            self.stdout.write(self.style.WARNING(f'Adding replies to {feedback_to_reply.count()} feedback entries...'))
            reply_count = 0
            for feedback_item in feedback_to_reply:
                try:
                    StaffReply.objects.create(
                        feedback=feedback_item,
                        user=random.choice(staff_users),
                        reply_text=random.choice(reply_texts)
                    )
                    reply_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to create reply for feedback {feedback_item.id}. Error: {e}'))
                if reply_count % 50 == 0:
                    self.stdout.write(f'{reply_count} replies added...')
            self.stdout.write(self.style.SUCCESS(f'Successfully added {reply_count} staff replies.'))
        else:
            self.stdout.write(self.style.WARNING('No eligible feedback or staff users available to add replies.'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))