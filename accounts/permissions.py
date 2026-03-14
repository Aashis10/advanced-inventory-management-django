from django.contrib.auth.decorators import user_passes_test


def _in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or _in_group(user, 'Admin'))


def is_staff_member(user):
    return user.is_authenticated and (is_admin(user) or _in_group(user, 'Staff'))


admin_required = user_passes_test(is_admin)
staff_required = user_passes_test(is_staff_member)
