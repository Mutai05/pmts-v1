from accounts.models import User
from departments.models import Department
from faker import Faker

def seed_users():
    fake = Faker()
    
    departments = Department.objects.all()
    if not departments.exists():
        print('Error: No departments found. Please seed departments first.')
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
        print('Created superuser: admin@county.gov')

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
            print(f'Created executive user: {email}')

    # Create departmental users
    for department in departments:
        email = f"{department.name.lower().replace(' ', '_')}@county.gov"
        if not User.objects.filter(email=email).exists():
            User.objects.create_user(
                email=email,
                password='dept123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='departmental',
                department=department
            )
            print(f'Created departmental head: {email}')

        # Create departmental staff
        for i in range(3):
            email = f"staff_{i}_{department.name.lower().replace(' ', '_')}@county.gov"
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='staff123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role='departmental',
                    department=department
                )
                print(f'Created departmental staff: {email}')

    # Create public users
    for _ in range(20):
        email = fake.email()
        if not User.objects.filter(email=email).exists():
            User.objects.create_user(
                email=email,
                password='public123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='public'
            )
            print(f'Created public user: {email}')

    print('Successfully seeded all user data')

# Run in shell:
# seed_users()