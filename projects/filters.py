import django_filters
from django.utils import timezone
from datetime import timedelta
from django.db import models

from .models import ProjectFeedback
from locations.models import SubCounty, Ward
from departments.models import Department

class FeedbackFilter(django_filters.FilterSet):
    # Time Range Filter Choices
    TIME_RANGE_CHOICES = (
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('year', 'This Year'),
        ('all', 'All Time'),
    )

    # Status Filter Choices (Combining flags)
    STATUS_CHOICES = (
        ('all', 'All (Excluding Flagged)'), # Default view
        ('flagged', 'Flagged Inappropriate'),
        ('reported', 'Reported Inappropriate'),
        ('flagged_or_reported', 'Flagged or Reported'),
    )

    # --- Field Filters --- #
    department = django_filters.ModelChoiceFilter(
        field_name='project__department',
        queryset=Department.objects.all(),
        label='Department'
    )
    sub_county = django_filters.ModelChoiceFilter(
        queryset=SubCounty.objects.all(),
        field_name='sub_county',
        label='Sub-County'
    )
    ward = django_filters.ModelChoiceFilter(
        queryset=Ward.objects.all(), # Will be dynamically filtered in the view/template if needed
        field_name='ward',
        label='Ward'
    )
    rating = django_filters.ChoiceFilter(
        choices=ProjectFeedback.RATING_CHOICES,
        label='Rating'
    )
    time_range = django_filters.ChoiceFilter(
        choices=TIME_RANGE_CHOICES,
        method='filter_by_time_range',
        label='Date Range',
        initial='month'
    )
    status = django_filters.ChoiceFilter(
        choices=STATUS_CHOICES,
        method='filter_by_status',
        label='Status'
    )

    class Meta:
        model = ProjectFeedback
        fields = ['department', 'sub_county', 'ward', 'rating', 'time_range', 'status']

    def __init__(self, *args, **kwargs):
        # Get user from view kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # --- Dynamic QuerySet Adjustments based on User --- #
        if self.user:
            if self.user.role == 'departmental':
                # Departmental user: Limit department filter choices & initial value
                if 'department' in self.filters:
                    dept_qs = Department.objects.filter(id=self.user.department_id)
                    self.filters['department'].queryset = dept_qs
                    self.filters['department'].initial = self.user.department
                    # Make department field hidden or readonly if desired
                    # self.filters['department'].widget = forms.HiddenInput()

        # --- Ward Dropdown Filtering (similar to forms) --- #
        if 'sub_county' in self.data:
             try:
                 subcounty_id = int(self.data.get('sub_county'))
                 if 'ward' in self.filters:
                     self.filters['ward'].queryset = Ward.objects.filter(subcounty_id=subcounty_id)
             except (ValueError, TypeError):
                 pass
        elif self.queryset.model == ProjectFeedback and 'ward' in self.filters:
            # If not filtering by sub-county, show all wards (or based on initial department if any)
            if self.user and self.user.role == 'departmental' and self.user.department:
                 # Optimization: Only show wards relevant to the user's department's projects?
                 # This could get complex. Showing all might be simpler for now.
                 pass # Keep queryset as Ward.objects.all() for now
            else:
                 pass # Keep queryset as Ward.objects.all() for now

    # --- Custom Filter Methods --- #
    def filter_by_time_range(self, queryset, name, value):
        now = timezone.now()
        if value == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif value == 'week':
            start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        elif value == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif value == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else: # 'all' or invalid
            return queryset
        return queryset.filter(created_at__gte=start_date)

    def filter_by_status(self, queryset, name, value):
        if value == 'flagged':
            return queryset.filter(flagged_inappropriate=True)
        elif value == 'reported':
            return queryset.filter(reported_inappropriate=True)
        elif value == 'flagged_or_reported':
            return queryset.filter(models.Q(flagged_inappropriate=True) | models.Q(reported_inappropriate=True))
        else: # 'all' (default - show non-flagged)
             # Note: The base queryset in the view should handle the default filtering
             # This filter method is mainly for selecting the *flagged* statuses.
            return queryset # Or apply default filter here if needed