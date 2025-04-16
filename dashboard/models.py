from django.db import models
from django.utils import timezone


class DashboardMetric(models.Model):
    """
    Model to store cached dashboard metrics for quicker dashboard loads.
    """
    name = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Dashboard Metric'
        verbose_name_plural = 'Dashboard Metrics'

    def __str__(self) -> str:
        return f"{self.name} Metric"

    def update_value(self, new_value):
        """Update metric value and timestamp."""
        self.value = new_value
        self.last_updated = timezone.now()
        self.save()
