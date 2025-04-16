from django.contrib import admin
from .models import Project, ProjectPhoto, ProjectProgress, ProjectFeedback, StaffReply, ProjectProgressPhoto, ProjectFeedbackAttachment, StaffReplyAttachment


class ProjectPhotoInline(admin.TabularInline):
    model = ProjectPhoto
    extra = 1


class ProjectProgressInline(admin.TabularInline):
    model = ProjectProgress
    extra = 0
    readonly_fields = ('updated_by',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model."""
    list_display = ('name', 'department', 'ward', 'status', 'percentage_complete', 'budget_allocation', 'financial_year')
    list_filter = ('status', 'department', 'ward__subcounty', 'financial_year')
    search_fields = ('name', 'description', 'contractor_name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProjectPhotoInline, ProjectProgressInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'department', 'ward', 'status')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'percentage_complete')
        }),
        ('Financial', {
            'fields': ('budget_allocation', 'expenditure', 'funding_source', 'financial_year')
        }),
        ('Implementation', {
            'fields': ('contractor_name', 'implementing_agency', 'google_map_location', 'challenges')
        }),
    )


@admin.register(ProjectPhoto)
class ProjectPhotoAdmin(admin.ModelAdmin):
    """Admin configuration for ProjectPhoto model."""
    list_display = ('project', 'caption', 'is_cover', 'upload_date')
    list_filter = ('is_cover', 'upload_date')
    search_fields = ('project__name', 'caption')
    raw_id_fields = ('project',)


@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    """Admin configuration for ProjectProgress model."""
    list_display = ('project', 'date', 'percentage', 'updated_by')
    list_filter = ('date',)
    search_fields = ('project__name', 'description')
    raw_id_fields = ('project',)
    readonly_fields = ('updated_by',)

    def save_model(self, request, obj, form, change):
        """Save the updated_by field with the current user."""
        if not obj.pk:  # Only set for new objects
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProjectFeedback)
class ProjectFeedbackAdmin(admin.ModelAdmin):
    """Admin configuration for ProjectFeedback model."""
    list_display = ('project', 'name', 'ward', 'rating', 'created_at', 'flagged_inappropriate', 'reported_inappropriate')
    list_filter = ('rating', 'flagged_inappropriate', 'reported_inappropriate', 'created_at', 'ward__subcounty', 'ward')
    search_fields = ('project__name', 'name', 'email', 'comment', 'id_number')
    actions = None


@admin.register(StaffReply)
class StaffReplyAdmin(admin.ModelAdmin):
    """Admin configuration for StaffReply model."""
    list_display = ('feedback', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('reply_text', 'feedback__comment', 'user__email')
    raw_id_fields = ('feedback', 'user') # Useful for selecting related objects


@admin.register(ProjectProgressPhoto)
class ProjectProgressPhotoAdmin(admin.ModelAdmin):
    """Admin configuration for ProjectProgressPhoto model."""
    list_display = ('progress_update', 'caption', 'upload_date')
    list_filter = ('upload_date',)
    search_fields = ('progress_update__project__name', 'caption')
    raw_id_fields = ('progress_update',)


@admin.register(ProjectFeedbackAttachment)
class ProjectFeedbackAttachmentAdmin(admin.ModelAdmin):
    """Admin configuration for ProjectFeedbackAttachment model."""
    list_display = ('feedback', 'file', 'is_image', 'upload_date')
    list_filter = ('is_image', 'upload_date')
    search_fields = ('feedback__name', 'feedback__comment', 'file')
    raw_id_fields = ('feedback',)


@admin.register(StaffReplyAttachment)
class StaffReplyAttachmentAdmin(admin.ModelAdmin):
    """Admin configuration for StaffReplyAttachment model."""
    list_display = ('reply', 'file', 'is_image', 'upload_date')
    list_filter = ('is_image', 'upload_date')
    search_fields = ('reply__reply_text', 'reply__user__email', 'file')
    raw_id_fields = ('reply',)
