import os
from django.core.files import File
from django.utils import timezone
from datetime import datetime, timedelta
from faker import Faker
from projects.models import (
    Project, ProjectPhoto, ProjectProgress, 
    ProjectProgressPhoto, ProjectFeedback,
    ProjectFeedbackAttachment, StaffReply,
    StaffReplyAttachment
)
from departments.models import Department
from locations.models import Ward, SubCounty
from accounts.models import User

fake = Faker()

def create_projects():
    # Clear existing data (optional)
    # Project.objects.all().delete()
    
    # Get required related objects
    departments = Department.objects.all()
    wards = Ward.objects.all()
    users = User.objects.filter(role__in=['departmental', 'executive'])
    
    if not departments or not wards or not users:
        print("Please seed Departments, Locations, and Users first!")
        return
    
    # Create sample projects
    projects = []
    for i in range(20):
        department = fake.random_element(departments)
        ward = fake.random_element(wards)
        start_date = fake.date_between(start_date='-1y', end_date='+1y')
        end_date = start_date + timedelta(days=fake.random_int(min=30, max=365))
        
        project = Project.objects.create(
            name=f"{department.name} {fake.word().title()} Project",
            description=fake.paragraph(nb_sentences=5),
            department=department,
            ward=ward,
            status=fake.random_element(Project.STATUS_CHOICES)[0],
            project_type=fake.random_element(Project.PROJECT_TYPE_CHOICES)[0],
            is_flagship=fake.boolean(chance_of_getting_true=20),
            start_date=start_date,
            end_date=end_date,
            percentage_complete=fake.random_int(min=0, max=100),
            budget_allocation=fake.random_number(digits=7),
            expenditure=fake.random_number(digits=6),
            funding_source=fake.random_element(Project.FUNDING_SOURCE_CHOICES)[0],
            contractor_name=fake.company() if fake.boolean() else None,
            contractor_phone=fake.phone_number() if fake.boolean() else None,
            contractor_email=fake.email() if fake.boolean() else None,
            contractor_address=fake.address() if fake.boolean() else None,
            implementing_agency=fake.company() if fake.boolean() else None,
            google_map_location=fake.url() if fake.boolean() else None,
            challenges=fake.paragraph(nb_sentences=2) if fake.boolean() else "",
            financial_year=f"{datetime.now().year}-{datetime.now().year+1}"
        )
        projects.append(project)
        
        # Create project photos
        for _ in range(fake.random_int(min=1, max=5)):
            ProjectPhoto.objects.create(
                project=project,
                image=None,  # You would add actual images in a real scenario
                caption=fake.sentence(),
                is_cover=True if _ == 0 else False
            )
        
        # Create progress updates
        progress_dates = [start_date + timedelta(days=x*30) for x in range(1, fake.random_int(min=1, max=6))]
        for i, date in enumerate(progress_dates):
            if date > timezone.now().date():
                continue  # Skip future dates
                
            progress = ProjectProgress.objects.create(
                project=project,
                date=date,
                percentage=min(100, (i+1)*20),  # Simple progression
                description=fake.paragraph(nb_sentences=3),
                updated_by=fake.random_element(users)
            )
            
            # Add progress photos
            for _ in range(fake.random_int(min=0, max=3)):
                ProjectProgressPhoto.objects.create(
                    progress_update=progress,
                    image=None,  # Add actual images in real scenario
                    caption=fake.sentence()
                )
    
    # Create project feedback
    for project in projects:
        for _ in range(fake.random_int(min=0, max=10)):
            ward = fake.random_element(wards)
            feedback = ProjectFeedback.objects.create(
                project=project,
                name=fake.name(),
                phone=fake.phone_number() if fake.boolean() else None,
                email=fake.email() if fake.boolean() else None,
                sub_county=ward.subcounty,
                ward=ward,
                id_number=str(fake.random_number(digits=8)),
                comment=fake.paragraph(nb_sentences=3),
                rating=fake.random_element(ProjectFeedback.RATING_CHOICES)[0],
                flagged_inappropriate=fake.boolean(chance_of_getting_true=5),
                reported_inappropriate=fake.boolean(chance_of_getting_true=5)
            )
            
            # Add feedback attachments
            if fake.boolean():
                ProjectFeedbackAttachment.objects.create(
                    feedback=feedback,
                    file=None,  # Add actual files in real scenario
                    caption=fake.sentence(),
                    is_image=fake.boolean()
                )
            
            # Add staff replies to some feedback
            if fake.boolean(chance_of_getting_true=30):
                reply = StaffReply.objects.create(
                    feedback=feedback,
                    user=fake.random_element(users),
                    reply_text=fake.paragraph(nb_sentences=4)
                )
                
                # Add reply attachments
                if fake.boolean():
                    StaffReplyAttachment.objects.create(
                        reply=reply,
                        file=None,  # Add actual files in real scenario
                        is_image=fake.boolean()
                    )
    
    print(f"Created {len(projects)} projects with related data")

if __name__ == "__main__":
    create_projects()