from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from products.models import ActivityLog

from .forms import StaffUserForm
from .permissions import admin_required


def login_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard:home')

	form = AuthenticationForm(request, data=request.POST or None)
	for field in form.fields.values():
		field.widget.attrs.update({'class': 'form-control'})
	if request.method == 'POST' and form.is_valid():
		auth_login(request, form.get_user())
		messages.success(request, 'Welcome back! Login successful.')
		return redirect('dashboard:home')

	return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
	logout(request)
	messages.info(request, 'You have been logged out.')
	return redirect('accounts:login')


@admin_required
def staff_list(request):
	staff_users = User.objects.filter(is_superuser=False).order_by('username')
	for user in staff_users:
		user.role_label = 'Admin' if user.groups.filter(name='Admin').exists() else 'Staff'
	return render(request, 'accounts/staff_list.html', {'staff_users': staff_users})


@admin_required
def staff_add(request):
	form = StaffUserForm(request.POST or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Staff account created successfully.')
		return redirect('accounts:staff_list')
	return render(request, 'accounts/staff_form.html', {'form': form, 'title': 'Add Staff Account'})


@admin_required
def staff_edit(request, pk):
	staff_user = get_object_or_404(User, pk=pk, is_superuser=False)
	form = StaffUserForm(request.POST or None, instance=staff_user)
	if form.is_valid():
		form.save()
		messages.success(request, 'Staff account updated successfully.')
		return redirect('accounts:staff_list')
	return render(request, 'accounts/staff_form.html', {'form': form, 'title': 'Edit Staff Account'})


@admin_required
def staff_delete(request, pk):
	staff_user = get_object_or_404(User, pk=pk, is_superuser=False)
	if request.method == 'POST':
		staff_user.delete()
		messages.warning(request, 'Staff account removed successfully.')
		return redirect('accounts:staff_list')
	return render(request, 'accounts/staff_confirm_delete.html', {'staff_user': staff_user})


@admin_required
def activity_log_view(request):
	activities = ActivityLog.objects.select_related('user', 'related_product').all()
	paginator = Paginator(activities, 20)
	page_obj = paginator.get_page(request.GET.get('page'))
	return render(request, 'accounts/activity_log.html', {'page_obj': page_obj})

# Create your views here.
