from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def should_show_sidebar(context):
    """Determines if the sidebar should be shown based on user role and current path."""
    request = context.get('request')
    user = context.get('user')

    if not request or not user or not user.is_authenticated:
        return False

    is_exec_or_dept = (
        getattr(user, 'is_executive', False) or
        getattr(user, 'is_departmental', False)
    )

    if not is_exec_or_dept:
        return False

    try:
        exec_dash_url = reverse('dashboard:executive_dashboard')
        dept_dash_url = reverse('dashboard:departmental_dashboard')
        feedback_url = reverse('projects:feedback_dashboard')
        profile_url = reverse('accounts:profile')
    except NoReverseMatch:
        return False

    is_on_dashboard_page = (
        request.path in [exec_dash_url, dept_dash_url, feedback_url])
    is_exec_or_dept = getattr(user, 'is_executive', False) or getattr(
        user, 'is_departmental', False)
    is_on_profile_page = (request.path in [profile_url] and is_exec_or_dept)

    display_sidebar = (
        is_on_dashboard_page or
        is_on_profile_page
    )

    return display_sidebar
