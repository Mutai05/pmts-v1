from django.shortcuts import render, get_object_or_404
from .models import Department, SubCounty, Project, Ward

def dashboard(request):
    context = {
        'total_projects': Project.objects.count(),
        'total_departments': Department.objects.count(),
        'total_subcounties': SubCounty.objects.count(),
        'total_wards': Ward.objects.count(),
        'completed_projects': Project.objects.filter(status='completed').count(),
        'ongoing_projects': Project.objects.filter(status='ongoing').count(),
        'stalled_projects': Project.objects.filter(status='stalled').count(),
        'subcounties': SubCounty.objects.all(),
    }
    return render(request, 'dashboard/index.html', context)

def all_departments(request):
    return render(request, 'dashboard/all-departments.html')

def subcounties(request):
    context = {
        'subcounties': SubCounty.objects.all(),
    }
    return render(request, 'dashboard/subcounties.html', context)

def projects(request):
    # Get filter parameters
    department_id = request.GET.get('department')
    sub_county_id = request.GET.get('sub_county')
    ward_id = request.GET.get('ward')
    status = request.GET.get('status')

    # Base queryset
    projects = Project.objects.select_related('department', 'sub_county', 'ward')

    # Apply filters
    if department_id:
        projects = projects.filter(department__id=department_id)
    if sub_county_id:
        projects = projects.filter(sub_county__id=sub_county_id)
    if ward_id:
        projects = projects.filter(ward__id=ward_id)
    if status:
        projects = projects.filter(status=status)

    context = {
        'projects': projects,
        'departments': Department.objects.all(),
        'subcounties': SubCounty.objects.all(),
        'wards': Ward.objects.all(),
        'department': department_id,
        'sub_county': sub_county_id,
        'ward': ward_id,
        'status': status,
    }
    return render(request, 'dashboard/projects.html', context)

def single_project(request, project_id):
    project = get_object_or_404(Project.objects.select_related('department', 'sub_county', 'ward'), id=project_id)
    context = {
        'project': project,
    }
    return render(request, 'dashboard/single-project.html', context)

def feedback(request):
    return render(request, 'dashboard/feedback.html')

def notifications(request):
    return render(request, 'dashboard/notifications.html')

def profile(request):
    return render(request, 'dashboard/profile.html')