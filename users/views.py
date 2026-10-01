from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser


def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_driver:
            return redirect('fleet:driver_portal')
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            if user.is_driver:
                return redirect('fleet:driver_portal')
            return redirect('dashboard:home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('users:login')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        city = request.POST.get('city', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, "Username and password are required.")
            return render(request, 'users/register.html', {'form_data': request.POST})

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/register.html', {'form_data': request.POST})

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'users/register.html', {'form_data': request.POST})

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, 'users/register.html', {'form_data': request.POST})

        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'users/register.html', {'form_data': request.POST})

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            city=city,
            role=CustomUser.Role.CUSTOMER,
        )
        login(request, user)
        messages.success(request, f"Account created! Welcome, {user.first_name or user.username}!")
        return redirect('dashboard:home')

    return render(request, 'users/register.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.phone_number = request.POST.get('phone_number', '').strip()
        request.user.city = request.POST.get('city', '').strip()
        request.user.address = request.POST.get('address', '').strip()
        request.user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('users:profile')

    return render(request, 'users/profile.html')


@login_required
def user_list(request):
    """Admin-only: list all users."""
    if not request.user.is_admin_user:
        messages.error(request, "You don't have permission to view user management.")
        return redirect('dashboard:home')
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'users/user_list.html', {
        'users': users,
        'role_choices': CustomUser.Role.choices,
    })


@login_required
def user_role_update(request, pk):
    """Admin-only: change a user's role."""
    if not request.user.is_admin_user:
        messages.error(request, "Permission denied.")
        return redirect('dashboard:home')
    target_user = CustomUser.objects.get(pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        target_user.role = new_role
        target_user.save()
        messages.success(request, f"{target_user.username}'s role updated to {target_user.get_role_display()}.")
    return redirect('users:user_list')
