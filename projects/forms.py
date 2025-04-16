from django import forms
from .models import Project, ProjectProgress, ProjectFeedback, ProjectPhoto, StaffReply
from locations.models import Ward, SubCounty


class ProjectForm(forms.ModelForm):
    """
    Form for creating and updating projects.
    """
    class Meta:
        model = Project
        fields = [
            # Basic Info
            'name', 'description', 'department', 'ward', 'status', 'project_type', 'is_flagship',
            # Timeline
            'start_date', 'end_date',
            # Financial
            'budget_allocation', 'expenditure',
            'funding_source', 'financial_year',
            # Implementation
            'contractor_name', 'contractor_phone', 'contractor_email', 'contractor_address',
            'implementing_agency', 'google_map_location', 'challenges'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'challenges': forms.Textarea(attrs={'rows': 3}),
            'contractor_address': forms.Textarea(attrs={'rows': 2}), # Smaller text area for address
            'project_type': forms.RadioSelect(), # Use radio buttons for type
        }
        labels = {
            'is_flagship': 'Flagship Project?',
        }
        help_texts = {
            'contractor_phone': model._meta.get_field('contractor_phone').help_text,
            'contractor_email': model._meta.get_field('contractor_email').help_text,
            'contractor_address': model._meta.get_field('contractor_address').help_text,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ward'].queryset = Ward.objects.none()

        # If subcounty is selected or instance has ward, filter wards
        if 'subcounty' in self.data:
            try:
                subcounty_id = int(self.data.get('subcounty'))
                self.fields['ward'].queryset = Ward.objects.filter(subcounty_id=subcounty_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.ward:
            self.fields['ward'].queryset = Ward.objects.filter(subcounty=self.instance.ward.subcounty)

        # Add subcounty field for filtering wards
        self.fields['subcounty'] = forms.ModelChoiceField(
            queryset=SubCounty.objects.all(),
            required=False,
            label="Sub-County"
        )

        # Set initial subcounty value if editing an existing project
        if self.instance.pk and self.instance.ward:
            self.fields['subcounty'].initial = self.instance.ward.subcounty


class ProjectProgressForm(forms.ModelForm):
    """
    Form for adding progress updates to a project.
    """
    class Meta:
        model = ProjectProgress
        fields = ['date', 'percentage', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ProjectFeedbackForm(forms.ModelForm):
    """
    Form for public users to submit feedback on projects.
    """
    sub_county = forms.ModelChoiceField(
        queryset=SubCounty.objects.all(),
        label="Sub-County",
        help_text="Select your Sub-County first to load Wards."
    )
    ward = forms.ModelChoiceField(
        queryset=Ward.objects.none(), # Initially empty
        label="Ward"
    )
    # Add a field for file uploads
    # attachments = forms.FileField(
    #     widget=forms.FileInput(attrs={'multiple': True}), # Use FileInput widget for multiple files
    #     required=False, # Make uploads optional
    #     label="Attach Photos/Files (Optional)",
    #     help_text="You can upload multiple relevant photos or documents."
    # )

    class Meta:
        model = ProjectFeedback
        fields = [
            'name', 'phone', 'email',
            'sub_county', 'ward', 'id_number',
            'comment', 'rating',
            # 'attachments' # Removed - handled in view
        ]
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
            'rating': forms.RadioSelect(),
            'name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'id_number': forms.TextInput(attrs={'inputmode': 'numeric'}),
        }
        # Add help texts based on model definitions
        help_texts = {
            'name': model._meta.get_field('name').help_text,
            'phone': model._meta.get_field('phone').help_text,
            'email': model._meta.get_field('email').help_text,
            'id_number': model._meta.get_field('id_number').help_text,
            'comment': model._meta.get_field('comment').help_text,
            'rating': model._meta.get_field('rating').help_text,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False # Make email optional in form
        self.fields['phone'].required = False # Make phone optional in form

        # Dependent dropdown logic for Ward based on SubCounty
        if 'sub_county' in self.data:
            try:
                subcounty_id = int(self.data.get('sub_county'))
                self.fields['ward'].queryset = Ward.objects.filter(subcounty_id=subcounty_id)
            except (ValueError, TypeError):
                pass # invalid input from browser; ignore and fallback to empty.
        elif self.instance.pk and self.instance.ward:
             # If editing an instance (though unlikely for public feedback)
             self.fields['sub_county'].initial = self.instance.ward.subcounty
             self.fields['ward'].queryset = Ward.objects.filter(subcounty=self.instance.ward.subcounty)

    def clean_id_number(self):
        # Additional check if needed, though regex validator handles format
        id_number = self.cleaned_data.get('id_number')
        # Example: Check against existing IDs if needed, but model unique=True handles this
        # if ProjectFeedback.objects.filter(id_number=id_number).exists():
        #     raise forms.ValidationError("This ID number has already been used to submit feedback.")
        return id_number


class ProjectPhotoForm(forms.ModelForm):
    """
    Form for uploading project photos.
    """
    class Meta:
        model = ProjectPhoto
        fields = ['image', 'caption', 'is_cover']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Optional caption'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True

    def clean_is_cover(self):
        is_cover = self.cleaned_data.get('is_cover')
        return is_cover


class StaffReplyForm(forms.ModelForm):
    """
    Form for staff to add replies to feedback.
    """
    class Meta:
        model = StaffReply
        fields = ['reply_text']
        widgets = {
            'reply_text': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Write your reply...',
                'class': 'block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border-gray-300 rounded-md'
                })
        }
        labels = {
            'reply_text': 'Your Reply'
        }
