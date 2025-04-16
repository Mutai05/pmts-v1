from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from departments.models import Department

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration.
    """
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = 'public'  # Default role for self-registration
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user profiles.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.TextInput(attrs={'readonly': True, 'required': False}),
        }


class StaffRegistrationForm(UserCreationForm):
    """
    Form for admin to register staff users.
    """
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=[('executive', 'Executive'), ('departmental', 'Departmental')])
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        help_text="Required for departmental users only"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'department', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        department = cleaned_data.get('department')

        if role == 'departmental' and not department:
            self.add_error('department', 'Department is required for departmental users')

        return cleaned_data
