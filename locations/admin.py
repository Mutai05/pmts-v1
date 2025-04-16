from django.contrib import admin
from .models import County, SubCounty, Ward


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    """Admin configuration for County model."""
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    """Admin configuration for SubCounty model."""
    list_display = ('name', 'county', 'created_at')
    list_filter = ('county',)
    search_fields = ('name', 'county__name')
    ordering = ('county', 'name')


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    """Admin configuration for Ward model."""
    list_display = ('name', 'subcounty', 'created_at')
    list_filter = ('subcounty', 'subcounty__county')
    search_fields = ('name', 'subcounty__name', 'subcounty__county__name')
    ordering = ('subcounty', 'name')
