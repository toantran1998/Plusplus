from django.contrib import admin
from django.contrib.admin.apps import SimpleAdminConfig
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from django.utils.translation import gettext as _

from app_config.settings import DEFAULT_DATE_TIME_FORMAT

LogEntry._meta.verbose_name_plural = _('Lịch sử hoạt động')
SimpleAdminConfig.verbose_name = 'Quản lý chung'


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "get_objects_link", "user", "get_action_flag"
                    , "get_action_time")

    def get_object_id(self, obj):
        return obj.object_id

    get_object_id.short_description = "ID"
    get_object_id.admin_order_field = "id"

    def get_objects_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>", url=str(obj.id) + '/change', url_display=obj.__str__())

    get_objects_link.short_description = "Hành động"
    get_objects_link.admin_order_field = "action_flag"

    def get_action_time(self, obj):
        return obj.action_time.strftime(DEFAULT_DATE_TIME_FORMAT)
    get_action_time.short_description = "Thời gian"
    get_action_time.admin_order_field = "action_time"

    def get_action_flag(self, obj):
        return obj.get_action_flag_display()

    get_action_flag.short_description = "Loại hành động"
    get_action_flag.admin_order_field = "action_flag"

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
    pass
