from django.db import models
from django.core.exceptions import ValidationError

class HeaderSettings(models.Model):
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    login_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if HeaderSettings.objects.exists() and not self.pk:
            raise ValidationError('Only one HeaderSettings instance is allowed.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Header Settings"

    class Meta:
        verbose_name = 'Header settings'
        verbose_name_plural = 'Header settings'

class FooterSettings(models.Model):
    cgtn_pmts_text = models.TextField(blank=True)
    about_text = models.TextField(blank=True)
    financial_years = models.JSONField(default=list)
    quick_links = models.JSONField(default=list)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_address = models.TextField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    copyright_year = models.CharField(max_length=4, blank=True)
    copyright_text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if FooterSettings.objects.exists() and not self.pk:
            raise ValidationError('Only one FooterSettings instance is allowed.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Footer Settings"

    class Meta:
        verbose_name = 'Footer settings'
        verbose_name_plural = 'Footer settings'

class PageSettings(models.Model):
    # About Page
    about_content = models.TextField(blank=True, help_text="General content for About page")
    intro_title = models.CharField(max_length=200, blank=True)
    intro_description = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    core_values = models.TextField(blank=True)
    # Objectives stored as JSON for simplicity (title, description, icon)
    objectives = models.JSONField(
        default=list,
        help_text="List of objectives with title, description, icon"
    )
    # FAQs stored as JSON (question, answer pairs)
    faqs = models.JSONField(
        default=list,
        help_text="List of FAQs with question and answer"
    )
    # Contact Page
    contact_address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_office_hours = models.CharField(max_length=200, blank=True)
    contact_departments = models.JSONField(
        default=list,
        help_text="List of departments with name and emails"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if PageSettings.objects.exists() and not self.pk:
            raise ValidationError('Only one PageSettings instance is allowed.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Page Settings"

    class Meta:
        verbose_name = 'Page settings'
        verbose_name_plural = 'Page settings'