from django.contrib import admin
from .models import Department, SubCounty, Ward, Project, Feedback, Notification, ActivityLog

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_count')
    search_fields = ('name',)

@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_count')
    search_fields = ('name',)

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_county')
    search_fields = ('name',)
    list_filter = ('sub_county',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'sub_county', 'status', 'budget_allocation', 'completion_percentage')
    list_filter = ('status', 'department', 'sub_county')
    search_fields = ('name',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('project', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('project__name', 'comment')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'created_at', 'read')
    list_filter = ('type', 'read', 'created_at')
    search_fields = ('title', 'message')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'project', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('message',)