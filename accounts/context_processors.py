def role_flags(request):
    user = getattr(request, 'user', None)
    is_admin_user = bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name='Admin').exists())
    )
    is_staff_user = bool(
        user
        and user.is_authenticated
        and (
            is_admin_user
            or user.groups.filter(name='Staff').exists()
            or user.is_staff
        )
    )
    return {
        'is_admin_user': is_admin_user,
        'is_staff_user': is_staff_user,
    }
