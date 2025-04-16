from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserUpdateForm

User = get_user_model()


def register(request):
    """
    Register a new user.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            messages.success(request, f'Account created for {email}')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """
    View and update user profile.
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user, initial={'email': request.user.email})
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)

    context = {
        'form': form
    }

    return render(request, 'accounts/profile.html', context)
