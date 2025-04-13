from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, default='bi-building')

    def __str__(self):
        return self.name

    @property
    def project_count(self):
        return self.project_set.count()

    @property
    def completed_count(self):
        return self.project_set.filter(status='Completed').count()

    @property
    def ongoing_count(self):
        return self.project_set.filter(status='Ongoing').count()

    @property
    def stalled_count(self):
        return self.project_set.filter(status='Stalled').count()

class SubCounty(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @property
    def project_count(self):
        return self.project_set.count()

    @property
    def completed_count(self):
        return self.project_set.filter(status='Completed').count()

    @property
    def ongoing_count(self):
        return self.project_set.filter(status='Ongoing').count()

    @property
    def stalled_count(self):
        return self.project_set.filter(status='Stalled').count()

class Ward(models.Model):
    name = models.CharField(max_length=100)
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Stalled', 'Stalled'),
    ]
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE, default=1)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ongoing')
    budget_allocation = models.DecimalField(max_digits=12, decimal_places=2)
    expenditure = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    completion_percentage = models.IntegerField(default=0)
    map_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.datetime(2025, 1, 1))
    updated_at = models.DateTimeField(default=timezone.datetime(2025, 1, 1))
    # New fields
    implementing_agency = models.CharField(max_length=100, blank=True, null=True, default='N/A')
    remarks = models.TextField(blank=True, null=True, default='None')
    contractor = models.CharField(max_length=100, blank=True, null=True, default='N/A')
    location = models.CharField(max_length=200, blank=True, null=True, default='N/A')
    financial_year = models.CharField(max_length=20, blank=True, null=True, default='N/A')
    source_of_funds = models.CharField(max_length=100, blank=True, null=True, default='N/A')
    description = models.TextField(blank=True, null=True, default='No description available')

    def __str__(self):
        return self.name

class ProjectPhoto(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='project_photos/', blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Photo for {self.project.name}"

class Feedback(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.project.name}"

class Notification(models.Model):
    TYPE_CHOICES = [
        ('alert', 'Alert'),
        ('info', 'Info'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class ActivityLog(models.Model):
    TYPE_CHOICES = [
        ('update', 'Project Update'),
        ('feedback', 'Feedback Submitted'),
        ('status', 'Status Change'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.created_at}"