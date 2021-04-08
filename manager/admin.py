from datetime import datetime

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.contrib import admin
from django.contrib.auth.apps import AuthConfig
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.utils.translation import gettext as _

from centre.models import Centre
from user.models import AuthUser

Group._meta.verbose_name_plural = _('Danh sách nhóm')
Group._meta.verbose_name = _('Danh sách nhóm')
AuthConfig.verbose_name = _("Nhóm & quyền")
Permission._meta.verbose_name_plural = _('Danh sách quyền')
Permission._meta.verbose_name = _('Danh sách quyền')
AuthUser._meta.verbose_name_plural = _('Tài khoản người dùng')


class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = 10

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if 'centre' in context['adminform'].form.fields and not request.user.is_superuser:
            context['adminform'].form.fields['centre'].choices = Centre.objects.filter(
                                                    id=request.user.centre.id).values_list('id', 'name')

        # if context['is_popup']:
        #     if 'groups' in context['adminform'].form.fields:
        #         context['adminform'].form.fields['groups'].disabled = True

        return super().render_change_form(request, context, add, change, form_url, obj)

    formfield_overrides = {
        models.DateField: {'widget': DatePickerInput(format='%d/%m/%Y')},
        models.DateTimeField: {'widget': DatePickerInput(format='%d/%m/%Y %H:%M:%S')},
        models.TimeField: {'widget': DatePickerInput(format='%H:%M')},
    }

    def lookup_allowed(self, lookup, *args, **kwargs):
        return True
        # if lookup == 'order__customer__id__exact':
        #     return True
        # return super(TaskAdmin, self).lookup_allowed(lookup, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_user = request.user
            obj.created_date_time = datetime.today()

        obj.updated_user = request.user
        obj.updated_date_time = datetime.today()

        return obj.save()

    def has_delete_permission(self, request, obj=None):
        return False
    pass


class BaseTabularInline(admin.TabularInline):
    extra = 0
    can_delete = True
    list_per_page = 10
    formfield_overrides = {
        models.DateField: {'widget': DatePickerInput(format='%d/%m/%Y')},
        models.DateTimeField: {'widget': DatePickerInput(format='%d/%m/%Y %H:%M:%S')},
        models.TimeField: {'widget': DatePickerInput(format='%H:%M')},
    }

    def has_delete_permission(self, request, obj=None):
        return False


class BaseStackedInline(admin.StackedInline):
    extra = 1
    can_delete = True
    formfield_overrides = {
        models.DateField: {'widget': DatePickerInput(format='%d/%m/%Y')},
        models.DateTimeField: {'widget': DatePickerInput(format='%d/%m/%Y %H:%M:%S')},
        models.TimeField: {'widget': DatePickerInput(format='%H:%M')},
    }

    def has_delete_permission(self, request, obj=None):
        return False


# admin.site.unregister(Permission)
# admin.site.unregister(Group)

# class PermissionAdmin(BaseModelAdmin):
#     list_display = ("id", "name_link", "codename")
#
#     def name_link(self, obj):
#         return format_html("<a href='{url}'>{url_display}</a>", url=str(obj.id) + '/change', url_display=obj.name)
#
#     name_link.short_description = _('Tiêu đề')
#     name_link.admin_order_field = 'name'
#
#     pass

