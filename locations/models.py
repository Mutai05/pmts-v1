from django.db import models

# Create your models here.

class County(models.Model):
    """
    Model representing a county.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'County'
        verbose_name_plural = 'Counties'

    def __str__(self) -> str:
        return f"{self.name} County"


class SubCounty(models.Model):
    """
    Model representing a sub-county within a county.
    """
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='subcounties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Sub County'
        verbose_name_plural = 'Sub Counties'
        unique_together = ['name', 'county']

    def __str__(self) -> str:
        return f"{self.name}, {self.county.name}"


class Ward(models.Model):
    """
    Model representing a ward within a sub-county.
    """
    name = models.CharField(max_length=100)
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='wards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ward'
        verbose_name_plural = 'Wards'
        unique_together = ['name', 'subcounty']

    def __str__(self) -> str:
        return f"{self.name}, {self.subcounty.name}"
