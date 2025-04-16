from django.db import models
from django.utils.text import slugify
from django.conf import settings
from departments.models import Department
from locations.models import Ward, SubCounty
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Project(models.Model):
    """
    Model representing a county project.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('stalled', 'Stalled'),
        ('under_procurement', 'Under Procurement'),
    ]

    FUNDING_SOURCE_CHOICES = [
        ('county', 'County'),
        ('national', 'National Government'),
        ('donor', 'Donor'),
    ]

    PROJECT_TYPE_CHOICES = [
        ('capital', 'Capital'),
        ('non_capital', 'Non-Capital'),
    ]

    # Basic Project Information
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='projects')
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT, related_name='projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='capital')
    is_flagship = models.BooleanField(default=False, help_text="Is this a flagship project?")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    percentage_complete = models.IntegerField(default=0)

    # Financial Information
    budget_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    expenditure = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    funding_source = models.CharField(max_length=20, choices=FUNDING_SOURCE_CHOICES, default='county')

    # Implementation Details
    contractor_name = models.CharField(max_length=255, blank=True, null=True)
    contractor_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Contractor phone number.")
    contractor_email = models.EmailField(blank=True, null=True, help_text="Contractor email address.")
    contractor_address = models.TextField(blank=True, null=True, help_text="Contractor office address.")
    implementing_agency = models.CharField(max_length=255, blank=True, null=True)
    google_map_location = models.URLField(blank=True, null=True)

    # Challenges
    challenges = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Financial Year (for filtering)
    financial_year = models.CharField(max_length=10, help_text="Format: YYYY-YYYY (e.g., 2023-2024)")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self) -> str:
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def subcounty(self):
        return self.ward.subcounty

    @property
    def county(self):
        return self.ward.subcounty.county

    @property
    def budget_utilization(self):
        if self.budget_allocation > 0:
            return (self.expenditure / self.budget_allocation) * 100
        return 0


class ProjectPhoto(models.Model):
    """
    Model for project photos.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='project_photos/%Y/%m/')
    caption = models.CharField(max_length=255, blank=True)
    is_cover = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Project Photo'
        verbose_name_plural = 'Project Photos'

    def __str__(self) -> str:
        return f"Photo for {self.project.name}"


class ProjectProgress(models.Model):
    """
    Model to track progress updates for a project.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='progress_updates')
    date = models.DateField()
    percentage = models.IntegerField()
    description = models.TextField()
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Project Progress'
        verbose_name_plural = 'Project Progress Updates'

    def __str__(self) -> str:
        return f"Progress update for {self.project.name} - {self.date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the project's percentage complete with the latest value
        project = self.project
        project.percentage_complete = self.percentage
        project.save(update_fields=['percentage_complete'])


class ProjectProgressPhoto(models.Model):
    """
    Model for storing photos related to a specific progress update.
    """
    progress_update = models.ForeignKey(ProjectProgress, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='progress_photos/%Y/%m/')
    caption = models.CharField(max_length=255, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Project Progress Photo'
        verbose_name_plural = 'Project Progress Photos'

    def __str__(self) -> str:
        return f"Photo for progress update on {self.progress_update.date} for {self.progress_update.project.name}"


class ProjectFeedback(models.Model):
    """
    Model for public feedback on projects.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='feedback')
    name = models.CharField(max_length=100, help_text="Your full name.")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="(Optional) Your phone number.")
    email = models.EmailField(blank=True, null=True, help_text="(Optional) Your email address.")

    sub_county = models.ForeignKey(SubCounty, on_delete=models.PROTECT, help_text="Select your Sub-County.")
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT, help_text="Select your Ward.")

    kenyan_id_validator = RegexValidator(
        regex=r'^[0-9]{7,8}$',
        message="Enter a valid ID number."
    )
    id_number = models.CharField(
        max_length=8,
        validators=[kenyan_id_validator],
        help_text="Your National ID number."
    )

    comment = models.TextField(help_text="Your feedback or comment about the project.")

    RATING_CHOICES = [
        (5, 'Very Satisfied'),
        (4, 'Satisfied'),
        (3, 'Neutral'),
        (2, 'Dissatisfied'),
        (1, 'Extremely Dissatisfied'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, default=3, help_text="Rate your satisfaction with the project.")

    flagged_inappropriate = models.BooleanField(default=False, help_text="Marked as potentially inappropriate by system/moderator.")
    reported_inappropriate = models.BooleanField(default=False, help_text="Reported as inappropriate by a user.")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project Feedback'
        verbose_name_plural = 'Project Feedback'

    def __str__(self) -> str:
        return f"Feedback on {self.project.name} by {self.name} (ID: ...{self.id_number})"


class ProjectFeedbackAttachment(models.Model):
    """
    Model for attachments (photos/files) submitted with project feedback.
    """
    feedback = models.ForeignKey(ProjectFeedback, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='feedback_attachments/%Y/%m/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional description of the attachment.")
    upload_date = models.DateTimeField(auto_now_add=True)

    # Common file formats for images
    is_image = models.BooleanField(default=False, help_text="Is this attachment an image?")

    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Feedback Attachment'
        verbose_name_plural = 'Feedback Attachments'

    def __str__(self) -> str:
        return f"Attachment for feedback by {self.feedback.name}"


class StaffReply(models.Model):
    """
    A reply from a staff member (Departmental or Executive) to a piece of public feedback.
    """
    feedback = models.ForeignKey(ProjectFeedback, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT, # Don't delete reply if user is deleted, maybe set to null/another user?
        limit_choices_to={'role__in': ['departmental', 'executive']},
        help_text="The staff member who wrote the reply."
    )
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Staff Reply'
        verbose_name_plural = 'Staff Replies'
        # Ensure only one reply per feedback? Or allow multiple?
        # unique_together = ('feedback', 'user') # Example if needed

    def __str__(self) -> str:
        return f"Reply by {self.user.get_full_name() or self.user.email} on {self.created_at.strftime('%Y-%m-%d')}"


class StaffReplyAttachment(models.Model):
    """
    Model for attachments (photos/files) submitted with a staff reply.
    """
    reply = models.ForeignKey(StaffReply, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/')
    upload_date = models.DateTimeField(auto_now_add=True)
    is_image = models.BooleanField(default=False, help_text="Is this attachment an image?")

    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Staff Reply Attachment'
        verbose_name_plural = 'Staff Reply Attachments'

    def __str__(self) -> str:
        return f"Attachment for reply by {self.reply.user.get_full_name() or self.reply.user.email}"
