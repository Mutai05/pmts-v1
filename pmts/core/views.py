from django.shortcuts import render
from .forms import ContactForm

def index(request):
    return render(request, 'core/index.html')

def about(request):
    return render(request, 'core/about.html')

def all_financial_years(request):
    return render(request, 'core/all_financial_years.html')

def fy_2022_2023(request):
    return render(request, 'core/fy_2022_2023.html')

def fy_2023_2024(request):
    return render(request, 'core/fy_2023_2024.html')

def fy_2024_2025(request):
    return render(request, 'core/fy_2024_2025.html')

def fy_2025_2026(request):
    return render(request, 'core/fy_2025_2026.html')

def fy_2026_2027(request):
    return render(request, 'core/fy_2026_2027.html')

def departments(request):
    return render(request, 'core/departments.html')

def gallery(request):
    departments = [
        {"name": "Department of Trade, Industrialization, Tourism & Cooperative Development"},
        {"name": "Department of Agriculture, Irrigation, Livestock & Fisheries"},
        {"name": "Department of Finance & Economic Planning"},
        {"name": "Department of Education & Technical Training"},
        {"name": "Department of Health Services & Sanitation"},
        {"name": "Department of Public Works, Transport & Energy"},
        {"name": "Department of Lands, Housing, Physical Planning & Urban Development"},
        {"name": "Department of Water, Environment, Natural Resources & Climate Change"},
        {"name": "Department of Gender, Youth, Sports & Culture"},
    ]
    return render(request, 'core/gallery.html', {'departments': departments})

def resources(request):
    resources = [
        {"title": "County Government Reports 2013/2014 - Trans-Nzoia County Assembly", "uploaded": "11/4/2022", "size": "200Kb", "file_url": "/static/files/report-2013-2014.pdf"},
        {"title": "Annual Development Plan 2024 - Trans-Nzoia", "uploaded": "03/15/2024", "size": "1.5Mb", "file_url": "/static/files/adp-2024.pdf"},
        {"title": "Budget Summary 2025 - Trans-Nzoia", "uploaded": "01/10/2025", "size": "500Kb", "file_url": "/static/files/budget-2025.pdf"},
        {"title": "Project Status Report Q1 2025", "uploaded": "04/01/2025", "size": "300Kb", "file_url": "/static/files/status-q1-2025.pdf"},
    ]
    return render(request, 'core/resources.html', {'resources': resources})

def faqs(request):
    return render(request, 'core/faqs.html')

def contact(request):
    if request.method == 'POST':
        # Handle form submission (e.g., save to database, send email)
        return render(request, 'core/contact.html', {'message': 'Message sent!'})
    return render(request, 'core/contact.html')