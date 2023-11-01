from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile
from .forms import UserChangeForm, UserCreationForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ('email',)

    list_filter = ('first_name',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions',
                                      'last_login', 'date_joined', 'phone_number', 'date_of_birth', 'is_email_verified')}),

    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )


admin.site.register(UserProfile, UserAdmin)
