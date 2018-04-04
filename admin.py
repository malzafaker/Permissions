# -*- coding: utf-8 -*-
from django.contrib import admin

from apps.permission.models import SecurityPermission


class UserListFilter(admin.SimpleListFilter):
    title = u'Наличие связи с пользователем'
    parameter_name = 'user'

    NOT_EXISTS = u'Нет_связи'

    def lookups(self, request, model_admin):
        return (
            (self.NOT_EXISTS, u'нет связи'),
        )

    def queryset(self, request, queryset):
        if self.value() == self.NOT_EXISTS:
            return queryset.filter(user=None)
        return queryset


@admin.register(SecurityPermission)
class SecurityPermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'user', 'get_user_full_name', 'approved', 'waiting', 'old_right')
    search_fields = ('user__last_name', 'user__first_name', 'user__middle_name', 'codename')
    list_filter = ('approved', 'waiting', 'old_right', UserListFilter)

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [field.name for field in obj._meta.many_to_many]
