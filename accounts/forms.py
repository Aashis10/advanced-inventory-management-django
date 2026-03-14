from django import forms
from django.contrib.auth.models import Group, User


class StaffUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    role = forms.ChoiceField(
        choices=(('Staff', 'Staff'), ('Admin', 'Admin')),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        role = self.cleaned_data.get('role', 'Staff')

        if password:
            user.set_password(password)

        if commit:
            user.save()
            for group_name in ['Staff', 'Admin']:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.remove(group)
            target_group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(target_group)

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['password'].help_text = 'Leave blank to keep current password.'
            self.fields['password'].required = False
            if self.instance.groups.filter(name='Admin').exists() or self.instance.is_superuser:
                self.fields['role'].initial = 'Admin'
            else:
                self.fields['role'].initial = 'Staff'
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = 'Required for new user.'
