from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q, Case, When, IntegerField, Value, OuterRef, Subquery, F, DecimalField
from django.db.models.functions import Coalesce
from projects.models import Project, ProjectFeedback
from departments.models import Department
from locations.models import Ward, SubCounty
from datetime import date
from decimal import Decimal


# Helper function for sentiment badges
def get_sentiment_badge(avg_rating):
    if avg_rating is None:
        return None, "bg-gray-100 text-gray-800"

    # Round to nearest integer for category mapping
    rounded_rating = int(round(avg_rating))

    # Get verbose name from RATING_CHOICES (handle potential missing rating)
    rating_dict = dict(ProjectFeedback.RATING_CHOICES)
    verbose_name = rating_dict.get(rounded_rating, f"Avg: {avg_rating:.1f}") # Fallback to avg number if rounded isn't in choices

    # Determine badge class based on rounded rating
    if rounded_rating == 5:
        badge_class = "bg-green-100 text-green-800"
    elif rounded_rating == 4:
        badge_class = "bg-blue-100 text-blue-800"
    elif rounded_rating == 3:
        badge_class = "bg-yellow-100 text-yellow-800"
    elif rounded_rating == 2:
        badge_class = "bg-orange-100 text-orange-800"
    elif rounded_rating == 1:
        badge_class = "bg-red-100 text-red-800"
    else:
        badge_class = "bg-gray-100 text-gray-800" # Default/fallback

    return verbose_name, badge_class


def get_current_financial_year():
    """ Calculates the current financial year string (e.g., '2023-2024'). Assumes July-June cycle. """
    today = date.today()
    if today.month >= 7:  # July onwards
        return f"{today.year}-{today.year + 1}"
    else:  # Before July
        return f"{today.year - 1}-{today.year}"


def get_current_term_info():
    """ Calculates the start year and label for the current 5-year election cycle. """
    current_year = date.today().year
    # Kenyan elections cycle usually starts August of years ending in 2 or 7.
    # Term Financial Years start from YYYY-(YYYY+1) of the election year.
    # Years ending 0, 1 belong to previous term (e.g. 2020, 2021 -> 2017 term)
    if current_year % 5 < 2:
        term_start_year = current_year - (current_year % 5) - 3
    # Years ending 2, 3, 4 belong to current term start (e.g. 2022, 2023, 2024 -> 2022 term)
    else:
        term_start_year = current_year - (current_year % 5) + 2

    term_value = f"term_{term_start_year}"
    term_label = f"Current Term ({term_start_year}-Present)"
    # The first FY string of the term
    term_start_fy_str = f"{term_start_year}-{term_start_year + 1}"
    return term_start_year, term_value, term_label, term_start_fy_str


def home(request):
    """
    Public homepage view showing basic information about the system.
    """
    # === Current Financial Year Stats ===
    current_fy = get_current_financial_year()
    current_fy_projects = Project.objects.filter(financial_year=current_fy)
    current_fy_allocation = current_fy_projects.aggregate(
        total=Sum('budget_allocation'))['total'] or 0
    current_fy_expenditure = current_fy_projects.aggregate(
        total=Sum('expenditure'))['total'] or 0

    if current_fy_allocation > 0:
        current_fy_absorption_rate = (
            current_fy_expenditure / current_fy_allocation) * 100
    else:
        current_fy_absorption_rate = 0

    current_fy_stats = {
        'year': current_fy,
        'allocation': current_fy_allocation,
        'expenditure': current_fy_expenditure,
        'absorption_rate': current_fy_absorption_rate,
    }

    # === Cumulative Term Stats ===
    term_start_year, term_value, term_label, term_start_fy_str = get_current_term_info()
    cumulative_projects = Project.objects.filter(
        financial_year__gte=term_start_fy_str)

    term_stats_raw = cumulative_projects.values('status').annotate(
        count=Count('id'),
        total_budget=Sum('budget_allocation')
    ).order_by('status')

    cumulative_term_stats = {
        'term': term_label,  # Use dynamic label
        'completed': {'count': 0, 'budget': 0},
        'ongoing': {'count': 0, 'budget': 0},
        'not_started': {'count': 0, 'budget': 0},
        'under_procurement': {'count': 0, 'budget': 0},
    }
    # Add stalled if it exists in the model choices and is needed here
    if hasattr(Project, 'STATUS_CHOICES') and any(s[0] == 'stalled' for s in Project.STATUS_CHOICES):
        cumulative_term_stats['stalled'] = {'count': 0, 'budget': 0}

    for stat in term_stats_raw:
        if stat['status'] in cumulative_term_stats:
            cumulative_term_stats[stat['status']]['count'] = stat['count']
            cumulative_term_stats[stat['status']
                                  ]['budget'] = stat['total_budget'] or 0

    # === Overall Stats (Existing) ===
    total_projects = Project.objects.count()
    completed_projects = Project.objects.filter(status='completed').count()
    ongoing_projects = Project.objects.filter(status='ongoing').count()
    departments = Department.objects.annotate(
        project_count=Count('projects')
    ).values('name', 'project_count').order_by('-project_count')[:5]

    context = {
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,
        'departments': departments,
        'current_fy_stats': current_fy_stats,
        'cumulative_term_stats': cumulative_term_stats,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard(request):
    """
    Main dashboard routing based on user role.
    """
    if request.user.role == 'executive':
        return redirect('dashboard:executive_dashboard')
    elif request.user.role == 'departmental':
        return redirect('dashboard:departmental_dashboard')
    else:
        return redirect('dashboard:home')


@login_required
def executive_dashboard(request):
    """
    Executive dashboard view for high-level overview of all projects.
    """
    if request.user.role != 'executive':
        return redirect('dashboard:home')

    today = date.today()

    # --- Get Filter Options --- #
    all_departments = Department.objects.all().order_by('name')
    all_subcounties = SubCounty.objects.all().order_by('name')
    all_wards = Ward.objects.all().order_by('subcounty__name', 'name') # Order for logical dropdown

    # --- Get Selected Filter Values --- #
    selected_department_id = request.GET.get('department')
    selected_subcounty_id = request.GET.get('subcounty')
    selected_ward_id = request.GET.get('ward')

    # --- Timeframe Filter Logic --- #
    all_financial_years = Project.objects.exclude(financial_year__isnull=True).exclude(financial_year='')\
                                        .values_list('financial_year', flat=True).distinct().order_by('-financial_year')
    term_start_year, current_term_value, current_term_label, current_term_start_fy = get_current_term_info()

    timeframe_choices = [
        ('all_time', 'All Time'),
        (current_term_value, current_term_label),
    ]
    timeframe_choices.extend([(f'fy_{fy}', f'FY {fy}') for fy in all_financial_years])

    selected_timeframe = request.GET.get('timeframe', current_term_value)

    # --- Filter Base Querysets --- #
    projects_qs = Project.objects.select_related('department', 'ward', 'ward__subcounty').all()
    feedback_qs = ProjectFeedback.objects.all() # Keep original for sentiment, filter later if needed

    # Apply Timeframe Filter
    current_timeframe_label_display = current_term_label
    if selected_timeframe.startswith('fy_'):
        fy_value = selected_timeframe.split('fy_')[1]
        projects_qs = projects_qs.filter(financial_year=fy_value)
        current_timeframe_label_display = f"FY {fy_value}"
    elif selected_timeframe == current_term_value:
        projects_qs = projects_qs.filter(financial_year__gte=current_term_start_fy)
        current_timeframe_label_display = current_term_label
    elif selected_timeframe == 'all_time':
        current_timeframe_label_display = "All Time"

    # --- Apply Location/Department Filters to projects_qs --- #
    if selected_department_id:
        projects_qs = projects_qs.filter(department_id=selected_department_id)
    if selected_subcounty_id:
        projects_qs = projects_qs.filter(ward__subcounty_id=selected_subcounty_id)
    if selected_ward_id:
        projects_qs = projects_qs.filter(ward_id=selected_ward_id)

    # --- Calculate Stats (Based on filtered projects_qs) --- #
    project_stats = {
        'total': projects_qs.count(),
        'completed': projects_qs.filter(status='completed').count(),
        'ongoing': projects_qs.filter(status='ongoing').count(),
        'stalled': projects_qs.filter(status='stalled').count(),
        'not_started': projects_qs.filter(status='not_started').count(),
        'under_procurement': projects_qs.filter(status='under_procurement').count(),
    }
    budget_aggregation = projects_qs.aggregate(
        total_allocation=Coalesce(Sum('budget_allocation'), Value(0, output_field=DecimalField())),
        total_expenditure=Coalesce(Sum('expenditure'), Value(0, output_field=DecimalField()))
    )
    budget_stats = {
        'total_allocation': budget_aggregation['total_allocation'],
        'total_expenditure': budget_aggregation['total_expenditure'],
    }
    if budget_stats['total_allocation'] > 0:
        budget_stats['absorption_rate'] = (
            budget_stats['total_expenditure'] / budget_stats['total_allocation']) * Decimal('100.0')
    else:
        budget_stats['absorption_rate'] = 0

    # Departmental Performance (Should probably reflect the overall data, not just filtered)
    # Re-calculate based on original projects for overall comparison, or adjust logic
    # For now, keeping the original calculation for overall view
    overall_projects_qs = Project.objects.all() # Use unfiltered for overall dept stats
    if selected_timeframe.startswith('fy_'):
        overall_projects_qs = overall_projects_qs.filter(financial_year=selected_timeframe.split('fy_')[1])
    elif selected_timeframe == current_term_value:
        overall_projects_qs = overall_projects_qs.filter(financial_year__gte=current_term_start_fy)

    # Start with base Department queryset
    departments_qs = Department.objects.all()
    # Apply department filter if selected
    if selected_department_id:
        departments_qs = departments_qs.filter(id=selected_department_id)

    # Now annotate the (potentially filtered) departments
    departments = departments_qs.annotate(
        project_count=Count('projects', filter=Q(projects__in=Subquery(overall_projects_qs.values('pk')))),
        total_budget=Coalesce(Sum('projects__budget_allocation', filter=Q(projects__in=Subquery(overall_projects_qs.values('pk')))), Value(0, output_field=DecimalField())),
        total_expenditure=Coalesce(Sum('projects__expenditure', filter=Q(projects__in=Subquery(overall_projects_qs.values('pk')))), Value(0, output_field=DecimalField())),
        avg_completion=Avg('projects__percentage_complete', filter=Q(projects__in=Subquery(overall_projects_qs.values('pk')))),
        absorption_rate_expr=Case(
            When(Q(total_budget=0) | Q(total_budget__isnull=True), then=Value(Decimal('0.0'), output_field=DecimalField())),
            default=(F('total_expenditure') * Decimal('100.0') / F('total_budget')),
            output_field=DecimalField()
        )
    ).order_by('-project_count')
    department_stats = list(departments.values(
        'id', 'name', 'project_count', 'total_budget', 'total_expenditure', 'avg_completion', 'absorption_rate_expr'
    ))

    # --- SubCounty Performance (based on timeframe AND filter) --- #
    # Start with base SubCounty queryset
    subcounties_qs = SubCounty.objects.all()
    # Apply subcounty filter if selected
    if selected_subcounty_id:
        subcounties_qs = subcounties_qs.filter(id=selected_subcounty_id)

    # Annotate the (potentially filtered) subcounties
    subcounty_stats = subcounties_qs.annotate(
        project_count=Count('wards__projects', filter=Q(wards__projects__in=Subquery(overall_projects_qs.values('pk')))),
        total_budget=Coalesce(Sum('wards__projects__budget_allocation', filter=Q(wards__projects__in=Subquery(overall_projects_qs.values('pk')))), Value(0, output_field=DecimalField())),
        total_expenditure=Coalesce(Sum('wards__projects__expenditure', filter=Q(wards__projects__in=Subquery(overall_projects_qs.values('pk')))), Value(0, output_field=DecimalField())),
        avg_completion=Avg('wards__projects__percentage_complete', filter=Q(wards__projects__in=Subquery(overall_projects_qs.values('pk')))),
         absorption_rate_expr=Case(
            When(Q(total_budget=0) | Q(total_budget__isnull=True), then=Value(Decimal('0.0'), output_field=DecimalField())),
            default=(F('total_expenditure') * Decimal('100.0') / F('total_budget')),
            output_field=DecimalField()
        )
    ).filter(project_count__gt=0).values(
         'id', 'name', 'project_count', 'total_budget', 'total_expenditure', 'avg_completion', 'absorption_rate_expr'
    ).order_by('-project_count')

    # --- Ward Performance (based on timeframe AND filter) --- #
    # Start with base Ward queryset
    wards_qs = Ward.objects.select_related('subcounty')
    # Apply ward filter if selected
    if selected_ward_id:
        wards_qs = wards_qs.filter(id=selected_ward_id)
    # Apply subcounty filter if selected (to show only wards in that subcounty)
    elif selected_subcounty_id:
         wards_qs = wards_qs.filter(subcounty_id=selected_subcounty_id)

    # Annotate the (potentially filtered) wards
    ward_stats = wards_qs.annotate(
        project_count=Count('projects', filter=Q(projects__in=Subquery(overall_projects_qs.values('pk')))),
        total_budget=Coalesce(Sum('projects__budget_allocation', filter=Q(projects__in=Subquery(overall_projects_qs.values('pk')))), Value(0, output_field=DecimalField())),
        total_expenditure=Coalesce(Sum('projects__expenditure', filter=Q(projects__in=Subquery(overall_projects_qs.values('pk')))), Value(0, output_field=DecimalField())),
        avg_completion=Avg('projects__percentage_complete', filter=Q(projects__in=Subquery(overall_projects_qs.values('pk')))),
         absorption_rate_expr=Case(
            When(Q(total_budget=0) | Q(total_budget__isnull=True), then=Value(Decimal('0.0'), output_field=DecimalField())),
            default=(F('total_expenditure') * Decimal('100.0') / F('total_budget')),
            output_field=DecimalField()
        )
    ).filter(project_count__gt=0).values(
        'id', 'name', 'subcounty__name', 'project_count', 'total_budget', 'total_expenditure', 'avg_completion', 'absorption_rate_expr'
    ).order_by('subcounty__name', 'name')

    # Project Health Indicators (Based on filtered projects_qs)
    delayed_projects = projects_qs.filter(
        ~Q(status='completed'), end_date__lt=today
    ).values('name', 'slug', 'department__name', 'status', 'end_date').order_by('end_date')
    stalled_projects = projects_qs.filter(
        status='stalled'
    ).values('name', 'slug', 'department__name').order_by('department__name', 'name')
    over_budget_projects = projects_qs.filter(
        expenditure__gt=F('budget_allocation')
    ).values('name', 'slug', 'department__name', 'budget_allocation', 'expenditure').order_by('department__name', 'name')

    # --- Financial Trend Data (Budget vs. Expenditure by FY - Based on filtered projects_qs) --- #
    financial_trend = projects_qs.values('financial_year')\
        .annotate(
            period_allocation=Sum('budget_allocation'),
            period_expenditure=Sum('expenditure')
        ).filter(financial_year__isnull=False).order_by('financial_year')

    # Prepare data for Chart.js (Convert Decimal to float)
    trend_labels = [item['financial_year'] for item in financial_trend]
    allocation_data = [float(item['period_allocation'] or 0) for item in financial_trend]
    expenditure_data = [float(item['period_expenditure'] or 0) for item in financial_trend]

    financial_trend_chart_data = {
        'labels': trend_labels,
        'allocation_data': allocation_data,
        'expenditure_data': expenditure_data,
    }

    # Citizen Sentiment
    # Start with base queryset and select related needed for filtering
    sentiment_feedback_qs = ProjectFeedback.objects.select_related('project__department', 'sub_county', 'ward').all()

    # Apply Timeframe Filter
    if selected_timeframe.startswith('fy_'):
        sentiment_feedback_qs = sentiment_feedback_qs.filter(project__financial_year=selected_timeframe.split('fy_')[1])
    elif selected_timeframe == current_term_value:
        sentiment_feedback_qs = sentiment_feedback_qs.filter(project__financial_year__gte=current_term_start_fy)

    # Apply Location/Department Filters
    if selected_department_id:
        sentiment_feedback_qs = sentiment_feedback_qs.filter(project__department_id=selected_department_id)
    if selected_subcounty_id:
        # Feedback model has direct relation to sub_county and ward
        sentiment_feedback_qs = sentiment_feedback_qs.filter(sub_county_id=selected_subcounty_id)
    if selected_ward_id:
        sentiment_feedback_qs = sentiment_feedback_qs.filter(ward_id=selected_ward_id)

    # Now calculate sentiment based on the fully filtered queryset
    sentiment_by_subcounty = sentiment_feedback_qs.values('sub_county_id', 'sub_county__name').annotate(
        avg_rating=Avg('rating')
    ).order_by('sub_county__name')

    # Process subcounty sentiment data for badges
    processed_sentiment_by_subcounty = []
    for subcounty_data in sentiment_by_subcounty:
        verbose_name, badge_class = get_sentiment_badge(subcounty_data.get('avg_rating'))
        subcounty_data['rating_verbose'] = verbose_name
        subcounty_data['rating_badge_class'] = badge_class
        processed_sentiment_by_subcounty.append(subcounty_data)

    # Process ward sentiment data for badges
    sentiment_by_ward = sentiment_feedback_qs.values('sub_county_id', 'sub_county__name', 'ward_id', 'ward__name').annotate(
        avg_rating=Avg('rating')
    ).order_by('sub_county__name', 'ward__name')
    processed_sentiment_by_ward = []
    for ward_data in sentiment_by_ward:
        verbose_name, badge_class = get_sentiment_badge(ward_data.get('avg_rating'))
        ward_data['rating_verbose'] = verbose_name
        ward_data['rating_badge_class'] = badge_class
        processed_sentiment_by_ward.append(ward_data)

    # --- Prepare Active Filters for Display --- #
    active_filters = []
    filter_params = request.GET
    filter_mapping = {
        'timeframe': 'Timeframe',
        'department': 'Department',
        'subcounty': 'Sub-County',
        'ward': 'Ward',
    }

    # Prepare lookups for names (convert querysets to dicts for faster lookup)
    department_lookup = {str(d.id): d.name for d in all_departments}
    subcounty_lookup = {str(s.id): s.name for s in all_subcounties}
    # Ward lookup needs special handling for display name
    ward_lookup = {str(w.id): f"{w.subcounty.name} - {w.name}" for w in all_wards}
    # Timeframe lookup uses existing dict (created earlier)
    timeframe_lookup = dict(timeframe_choices)

    for key, value in filter_params.items():
        if value and key in filter_mapping:
            label = filter_mapping[key]
            display_value = value # Default

            if key == 'timeframe':
                display_value = timeframe_lookup.get(value, value)
                # Don't show the default timeframe as an "active" filter unless explicitly chosen?
                # if value == current_term_value and 'timeframe' not in request.GET:
                #     continue # Skip if it's the default and wasn't in GET params
            elif key == 'department':
                display_value = department_lookup.get(value, f"ID: {value}")
            elif key == 'subcounty':
                display_value = subcounty_lookup.get(value, f"ID: {value}")
            elif key == 'ward':
                display_value = ward_lookup.get(value, f"ID: {value}")

            # Only add if display_value is meaningful
            if display_value:
                 active_filters.append({
                     'key': key,
                     'label': label,
                     'value': display_value
                 })

    context = {
        'project_stats': project_stats,
        'budget_stats': budget_stats,
        'department_stats': department_stats,
        'delayed_projects': delayed_projects,
        'stalled_projects': stalled_projects,
        'over_budget_projects': over_budget_projects,
        'sentiment_by_subcounty': processed_sentiment_by_subcounty,
        'sentiment_by_ward': processed_sentiment_by_ward,
        'timeframe_choices': timeframe_choices,
        'selected_timeframe': selected_timeframe,
        'current_timeframe_label': current_timeframe_label_display,
        # Add filter options and selections
        'all_departments': all_departments,
        'all_subcounties': all_subcounties,
        'all_wards': all_wards,
        'selected_department_id': selected_department_id,
        'selected_subcounty_id': selected_subcounty_id,
        'selected_ward_id': selected_ward_id,
        # Add financial trend chart data
        'financial_trend_chart_data': financial_trend_chart_data,
        'active_filters': active_filters, # Add the active filters list
        # Add Subcounty and Ward stats
        'subcounty_stats': subcounty_stats,
        'ward_stats': ward_stats,
    }

    return render(request, 'dashboard/executive_dashboard.html', context)


@login_required
def departmental_dashboard(request):
    """
    Departmental dashboard view for department-specific projects.
    """
    if request.user.role != 'departmental' or not request.user.department:
        return redirect('dashboard:home')

    department = request.user.department
    today = date.today()

    # --- Timeframe Filter Logic (Copied & Adapted from Executive) --- #
    all_financial_years = Project.objects.exclude(financial_year__isnull=True).exclude(financial_year='')\
                                        .values_list('financial_year', flat=True).distinct().order_by('-financial_year')
    term_start_year, current_term_value, current_term_label, current_term_start_fy = get_current_term_info()

    timeframe_choices = [
        ('all_time', 'All Time'),
        (current_term_value, current_term_label),
    ]
    timeframe_choices.extend([(f'fy_{fy}', f'FY {fy}') for fy in all_financial_years])

    selected_timeframe = request.GET.get('timeframe', current_term_value)

    # --- Filter Base Queryset (Department First) --- #
    projects_qs = Project.objects.select_related('ward', 'ward__subcounty').filter(department=department)

    # --- Apply Timeframe Filter --- #
    current_timeframe_label_display = current_term_label
    if selected_timeframe.startswith('fy_'):
        fy_value = selected_timeframe.split('_')[1]
        projects_qs = projects_qs.filter(financial_year=fy_value)
        current_timeframe_label_display = f"FY {fy_value}"
    elif selected_timeframe == current_term_value:
        projects_qs = projects_qs.filter(financial_year__gte=current_term_start_fy)
        current_timeframe_label_display = current_term_label
    elif selected_timeframe == 'all_time':
        # No additional year filter needed
        current_timeframe_label_display = "All Time"
    # If default was used and GET param wasn't set, filter is already applied

    # Project stats (Based on filtered projects_qs)
    project_stats = {
        'total': projects_qs.count(),
        'completed': projects_qs.filter(status='completed').count(),
        'ongoing': projects_qs.filter(status='ongoing').count(),
        'stalled': projects_qs.filter(status='stalled').count(),
        'not_started': projects_qs.filter(status='not_started').count(),
        'under_procurement': projects_qs.filter(status='under_procurement').count(),
    }

    # Budget stats
    budget_aggregation = projects_qs.aggregate(
        total_allocation=Coalesce(Sum('budget_allocation'), Value(0, output_field=DecimalField())),
        total_expenditure=Coalesce(Sum('expenditure'), Value(0, output_field=DecimalField()))
    )
    budget_stats = {
        'total_allocation': budget_aggregation['total_allocation'],
        'total_expenditure': budget_aggregation['total_expenditure'],
    }

    # Calculate budget absorption rate
    if budget_stats['total_allocation'] > 0:
        budget_stats['absorption_rate'] = (
            budget_stats['total_expenditure'] / budget_stats['total_allocation']) * Decimal('100.0')
    else:
        budget_stats['absorption_rate'] = 0

    # Project Health Indicators (Based on filtered projects_qs)
    delayed_projects = projects_qs.filter(
        ~Q(status='completed'), end_date__lt=today
    ).values('name', 'slug', 'status', 'end_date', 'percentage_complete').order_by('end_date')

    stalled_projects = projects_qs.filter(
        status='stalled'
    ).values('name', 'slug', 'percentage_complete', 'updated_at').order_by('-updated_at')

    over_budget_projects = projects_qs.filter(
        expenditure__gt=F('budget_allocation')
    ).values('name', 'slug', 'budget_allocation', 'expenditure', 'percentage_complete').order_by(F('expenditure')-F('budget_allocation')).reverse()

    # --- Financial Trend Data (Budget vs. Expenditure by FY) --- #
    # Group by financial_year within the already timeframe-filtered projects_qs
    financial_trend = projects_qs.values('financial_year')\
        .annotate(
            period_allocation=Sum('budget_allocation'),
            period_expenditure=Sum('expenditure')
        ).filter(financial_year__isnull=False).order_by('financial_year')

    # Prepare data for Chart.js
    trend_labels = [item['financial_year'] for item in financial_trend]
    # Convert Decimal to float for JavaScript compatibility
    allocation_data = [float(item['period_allocation'] or 0) for item in financial_trend]
    expenditure_data = [float(item['period_expenditure'] or 0) for item in financial_trend]

    financial_trend_chart_data = {
        'labels': trend_labels,
        'allocation_data': allocation_data,
        'expenditure_data': expenditure_data,
    }

    # Data for Status Chart (consider if needed or remove if template changes)
    status_chart_data = {
        'labels': ['Completed', 'Ongoing', 'Stalled', 'Not Started', 'Procurement'],
        'data': [
            project_stats['completed'],
            project_stats['ongoing'],
            project_stats['stalled'],
            project_stats['not_started'],
            project_stats['under_procurement']
        ],
        'colors': ['#10B981', '#3B82F6', '#EF4444', '#6B7280', '#06B6D4'] # Use theme colors
    }

    context = {
        'department': department,
        'project_stats': project_stats,
        'budget_stats': budget_stats,
        'delayed_projects': delayed_projects,
        'stalled_projects': stalled_projects,
        'over_budget_projects': over_budget_projects,
        'timeframe_choices': timeframe_choices,
        'selected_timeframe': selected_timeframe,
        'current_timeframe_label': current_timeframe_label_display,
        'all_financial_years': all_financial_years, # Pass for filter dropdown
        'current_term_value': current_term_value, # Pass for filter dropdown
        'current_term_label': current_term_label, # Pass for filter dropdown
        'status_chart_data': status_chart_data, # Pass chart data
        'remaining_budget': budget_stats['total_allocation'] - budget_stats['total_expenditure'], # Pass remaining budget
        'financial_trend_chart_data': financial_trend_chart_data, # Pass financial trend data
    }

    return render(request, 'dashboard/departmental_dashboard.html', context)


def public_dashboard(request):
    """
    Public dashboard with filterable statistics.
    """
    # === Dynamic Term Info ===
    term_start_year, current_term_value, current_term_label, current_term_start_fy = get_current_term_info()

    # === Filter Logic ===
    timeframe = request.GET.get('timeframe', current_term_value)  # Default to current_term_value
    selected_fy = None
    filter_start_fy = None

    if timeframe.startswith('fy_'):
        selected_fy = timeframe.split('_')[1]
        current_timeframe_label = f"Financial Year {selected_fy}"
    elif timeframe == current_term_value:
        filter_start_fy = current_term_start_fy
        current_timeframe_label = current_term_label
    elif timeframe == 'all_time':
        # No year filter needed
        current_timeframe_label = "All Time"
    else:  # Default to current_term_value
        timeframe = current_term_value  # Ensure timeframe variable is consistent
        current_timeframe_label = current_term_label

    # Base queryset based on timeframe
    projects_qs = Project.objects.all()
    if selected_fy:
        projects_qs = projects_qs.filter(financial_year=selected_fy)
    elif filter_start_fy:
        projects_qs = projects_qs.filter(financial_year__gte=filter_start_fy)
    # No filter needed for all_time

    # --- Project Status Definitions --- #
    # Define status filters once to avoid repetition
    status_filters = {
        'completed': Q(status='completed'),
        'ongoing': Q(status='ongoing'),
        'not_started': Q(status='not_started'),
        'stalled': Q(status='stalled'),
        'under_procurement': Q(status='under_procurement'),
    }
    status_budget_filters = {f"{status}_budget": Sum(
        'budget_allocation', filter=q) for status, q in status_filters.items()}
    status_count_filters = {f"{status}_count": Count(
        'id', filter=q) for status, q in status_filters.items()}

    # === Quick Stats ===
    quick_stats_raw = projects_qs.aggregate(
        total_projects=Count('id'),
        total_budget=Sum('budget_allocation'),
        **status_count_filters,
        **status_budget_filters
    )
    quick_stats = {
        'all': {'count': quick_stats_raw['total_projects'] or 0, 'budget': quick_stats_raw['total_budget'] or 0},
        **{status: {'count': quick_stats_raw[f'{status}_count'] or 0,
                    'budget': quick_stats_raw[f'{status}_budget'] or 0}
           for status in status_filters}
    }

    # === Projects Per Department ===
    department_status_subqueries = {}
    for status, status_q in status_filters.items():
        department_status_subqueries[f'{status}_count'] = Coalesce(
            Subquery(
                projects_qs.filter(
                    department_id=OuterRef('pk')).filter(status_q)
                .values('department_id').annotate(c=Count('id')).values('c')[:1]
            ), 0, output_field=IntegerField()
        )
    departments_stats = Department.objects.annotate(
        total_projects=Coalesce(
            Subquery(
                projects_qs.filter(department_id=OuterRef('pk'))
                           .values('department_id').annotate(c=Count('id')).values('c')[:1]
            ), 0, output_field=IntegerField()
        ),
        **department_status_subqueries
    ).values(
        'id', 'name', 'total_projects',
        # Dynamically add all status counts
        *[f'{status}_count' for status in status_filters]
    ).order_by('name')

    # === Projects Per Sub-County ===
    subcounty_stats = SubCounty.objects.annotate(
        project_count=Coalesce(
            Subquery(
                projects_qs.filter(ward__subcounty_id=OuterRef('pk'))
                           .values('ward__subcounty_id').annotate(c=Count('id')).values('c')[:1]
            ), 0, output_field=IntegerField()
        ),
        total_budget=Coalesce(
            Subquery(
                projects_qs.filter(ward__subcounty_id=OuterRef('pk'))
                           .values('ward__subcounty_id').annotate(s=Sum('budget_allocation')).values('s')[:1]
            ), 0, output_field=IntegerField()
        )
    ).filter(project_count__gt=0).values(
        'id', 'name', 'project_count', 'total_budget'
    ).order_by('name')

    # === Projects Per Ward ===
    # Annotate counts per status for each ward
    ward_status_subqueries = {}
    for status, status_q in status_filters.items():
        ward_status_subqueries[f'{status}_count'] = Coalesce(
            Subquery(
                projects_qs.filter(ward_id=OuterRef('pk')).filter(status_q)
                           .values('ward_id').annotate(c=Count('id')).values('c')[:1]
            ), 0, output_field=IntegerField()
        )

    ward_stats = Ward.objects.select_related('subcounty').annotate(
        project_count=Coalesce(  # Total count
            Subquery(
                projects_qs.filter(ward_id=OuterRef('pk'))
                           .values('ward_id').annotate(c=Count('id')).values('c')[:1]
            ), 0, output_field=IntegerField()
        ),
        total_budget=Coalesce(  # Total budget
            Subquery(
                projects_qs.filter(ward_id=OuterRef('pk'))
                           .values('ward_id').annotate(s=Sum('budget_allocation')).values('s')[:1]
            ), 0, output_field=IntegerField()
        ),
        **ward_status_subqueries  # Add counts for each status
    ).filter(project_count__gt=0).values(
        'id', 'name', 'subcounty_id', 'subcounty__name', 'project_count', 'total_budget',
        # Include status counts in values
        *[f'{status}_count' for status in status_filters]
    ).order_by('subcounty__name', 'name')

    # Group wards by subcounty (structure remains the same, ward dicts have more data)
    wards_by_subcounty = {}
    for ward in ward_stats:
        subcounty_name = ward['subcounty__name']
        if subcounty_name not in wards_by_subcounty:
            wards_by_subcounty[subcounty_name] = []
        wards_by_subcounty[subcounty_name].append(ward)

    # === Filter Options ===
    all_financial_years = Project.objects.exclude(financial_year__isnull=True).exclude(financial_year='')\
                                         .values_list('financial_year', flat=True).distinct().order_by('-financial_year')

    context = {
        'quick_stats': quick_stats,
        'departments_stats': departments_stats,
        'subcounty_stats': subcounty_stats,
        'wards_by_subcounty': wards_by_subcounty,
        'all_financial_years': all_financial_years,
        'current_term_value': current_term_value,
        'current_term_label': current_term_label,
        'current_timeframe': timeframe,
        'current_timeframe_label': current_timeframe_label,
        'status_badges': {
            'completed_count': {'label': 'Completed', 'class': 'bg-green-100 text-green-800'},
            'ongoing_count': {'label': 'Ongoing', 'class': 'bg-blue-100 text-blue-800'},
            'not_started_count': {'label': 'Not Started', 'class': 'bg-gray-100 text-gray-800'},
            'stalled_count': {'label': 'Stalled', 'class': 'bg-red-100 text-red-800'},
            'under_procurement_count': {'label': 'Procurement', 'class': 'bg-cyan-100 text-cyan-800'}
        }
        # Pass status definitions to template if needed for badge labels/classes
        # 'project_statuses': Project.STATUS_CHOICES
    }
    return render(request, 'dashboard/public_dashboard.html', context)
