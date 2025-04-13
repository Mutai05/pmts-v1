from django.contrib import admin
from django.db import models
from django import forms
from .models import HeaderSettings, FooterSettings, PageSettings
from django_jsonform.widgets import JSONFormWidget

# JSON schemas for array fields
OBJECTIVES_JSON_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'title': {'type': 'string', 'title': 'Objective Title'},
            'description': {'type': 'string', 'title': 'Description'},
            'icon': {'type': 'string', 'title': 'Icon Class (e.g., bi-eye-fill)'},
        },
        'required': ['title', 'description'],
    },
}

FAQS_JSON_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'question': {'type': 'string', 'title': 'Question'},
            'answer': {'type': 'string', 'title': 'Answer'},
        },
        'required': ['question', 'answer'],
    },
}

DEPARTMENTS_JSON_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'title': 'Department Name'},
            'emails': {
                'type': 'array',
                'title': 'Email(s)',
                'items': {'type': 'string'},
            },
        },
        'required': ['name', 'emails'],
    },
}

FOOTER_JSON_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'text': {'type': 'string', 'title': 'Text'},
            'url': {'type': 'string', 'title': 'URL'},
        },
        'required': ['text', 'url'],
    },
}

class CustomJSONFormWidget(JSONFormWidget):
    def render_field(self, name, value, schema, attrs=None):
        attrs = attrs or {}
        if name in ['answer', 'description']:
            attrs.update({'rows': 6, 'cols': 80, 'class': 'vLargeTextField'})
            widget = forms.Textarea(attrs=attrs)
        else:
            attrs.update({'class': 'vTextField'})
            widget = forms.TextInput(attrs=attrs)
        return widget.render(name, value, attrs)

class FooterSettingsForm(forms.ModelForm):
    cgtn_pmts_text = forms.CharField(
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False,
        label='CGTN PMTS Text'
    )

    class Meta:
        model = FooterSettings
        fields = '__all__'
        widgets = {
            'financial_years': JSONFormWidget(schema=FOOTER_JSON_SCHEMA),
            'quick_links': JSONFormWidget(schema=FOOTER_JSON_SCHEMA),
            'about_text': forms.Textarea(attrs={'rows': 6, 'cols': 80}),
            'contact_address': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'copyright_text': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
        }

class PageSettingsForm(forms.ModelForm):
    intro_title = forms.CharField(
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False,
        label='Introduction Title'
    )
    intro_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 80}),
        required=False,
        label='Introduction Description'
    )
    mission = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 80}),
        required=False,
        label='Mission'
    )
    vision = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 80}),
        required=False,
        label='Vision'
    )
    core_values = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 80}),
        required=False,
        label='Core Values'
    )
    contact_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 80}),
        required=False,
        label='Address'
    )
    contact_email = forms.EmailField(
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False,
        label='Email'
    )
    contact_phone = forms.CharField(
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False,
        label='Phone'
    )
    contact_office_hours = forms.CharField(
        widget=forms.TextInput(attrs={'size': '80'}),
        required=False,
        label='Office Hours'
    )

    class Meta:
        model = PageSettings
        fields = '__all__'
        widgets = {
            'objectives': CustomJSONFormWidget(schema=OBJECTIVES_JSON_SCHEMA),
            'faqs': CustomJSONFormWidget(schema=FAQS_JSON_SCHEMA),
            'contact_departments': JSONFormWidget(schema=DEPARTMENTS_JSON_SCHEMA),
        }

@admin.register(HeaderSettings)
class HeaderSettingsAdmin(admin.ModelAdmin):
    list_display = ('updated_at',)
    def has_add_permission(self, request):
        return not HeaderSettings.objects.exists()

@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    form = FooterSettingsForm
    list_display = ('updated_at',)
    fieldsets = (
        ('CGTN PMTS & About', {'fields': ('cgtn_pmts_text', 'about_text')}),
        ('Financial Years', {'fields': ('financial_years',)}),
        ('Quick Links', {'fields': ('quick_links',)}),
        ('Contact Details', {'fields': ('contact_phone', 'contact_email', 'contact_address')}),
        ('Social Links', {'fields': ('twitter_url', 'facebook_url', 'instagram_url')}),
        ('Copyright', {'fields': ('copyright_year', 'copyright_text')}),
    )
    def has_add_permission(self, request):
        return not FooterSettings.objects.exists()

@admin.register(PageSettings)
class PageSettingsAdmin(admin.ModelAdmin):
    form = PageSettingsForm
    list_display = ('updated_at',)
    fieldsets = (
        ('About Page', {
            'fields': (
                'intro_title',
                'intro_description',
                'mission',
                'vision',
                'core_values',
                'objectives'
            ),
            'description': 'Manage content for the About page, including introduction, mission, vision, core values, and objectives.'
        }),
        ('FAQs Page', {
            'fields': ('faqs',),
            'description': 'Manage FAQ questions and answers.'
        }),
        ('Contact Page', {
            'fields': (
                'contact_address',
                'contact_email',
                'contact_phone',
                'contact_office_hours',
                'contact_departments'
            ),
            'description': 'Manage contact details and department emails.'
        }),
    )
    def has_add_permission(self, request):
        return not PageSettings.objects.exists()