from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html

from app_config import settings
from app_config.settings import DEFAULT_DATE_TIME_FORMAT
from manager.admin import BaseModelAdmin
from message.models import Notification, EmailInbox
from user.models import AuthUser


@admin.register(EmailInbox)
class EmailInboxAdmin(BaseModelAdmin):
    list_display = ("id", "get_subject_link", "from_email"
                    , "to_email", "get_email_content", "get_sent_date_time"
                    , "state")
    search_fields = ['subject', 'to_email', "content", "state"]
    list_filter = ("from_email", "to_email", "state",)

    def get_subject_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.subject)
    get_subject_link.short_description = 'Tiêu đề'
    get_subject_link.admin_order_field = 'subject'

    def get_sent_date_time(self, obj):
        if obj.sent_date_time:
            return obj.sent_date_time.strftime(DEFAULT_DATE_TIME_FORMAT)
    get_sent_date_time.short_description = 'Ngày gửi'
    get_sent_date_time.admin_order_field = 'sent_date_time'

    def get_email_content(self, obj):
        return obj.content
    get_email_content.short_description = 'Nội dung'
    get_email_content.admin_order_field = 'content'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return EmailInbox.objects.filter(Q(from_email=request.user.email) | Q(to_email=request.user.email))

    # def get_list_filter(self, request):
    #     filters = self.list_filter
    #     if request.user.is_superuser:
    #         filters = ("centre",) + filters
    #
    #     return filters

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    pass


@admin.register(Notification)
class NotificationAdmin(BaseModelAdmin):
    list_display = ("id", "title_link", "to_user_id", "get_notification_content", "get_sent_date", "get_viewed_state")

    def title_link(self, obj):
        if not obj.viewed_state:
            return format_html("<a href='{url}' class='notification_title_link' id={title_link_id}><b>{url_display}</b></a>",
                               url=str(obj.id) + '/change',
                               url_display=obj.title,
                               title_link_id=str(obj.id))
        return format_html("<a href='{url}' class='notification_title_link' id={title_link_id}>{url_display}</a>",
                           url=str(obj.id) + '/change',
                           url_display=obj.title,
                           title_link_id=str(obj.id))
    title_link.short_description = "Tiêu đề"
    title_link.admin_order_field = "title"

    # def get_to_user(self, obj):
    #     return AuthUser.objects.get(id=obj.to_user_id).full_name
    # get_to_user.short_description = "Người nhận"
    # get_to_user.admin_order_field = "to_user_id"

    def get_notification_content(self, obj):
        return obj.content
    get_notification_content.short_description = 'Nội dung'
    get_notification_content.admin_order_field = 'content'

    def get_sent_date(self, obj):
        return obj.sent_date.strftime(settings.DEFAULT_DATE_TIME_FORMAT)
    get_sent_date.short_description = "Ngày gửi"

    def get_viewed_state(self, obj):
        if obj.viewed_state:
            return 'Đã xem'
        return 'Chưa xem'
    get_viewed_state.short_description = "Trạng thái"
    get_viewed_state.admin_order_field = "viewed_state"

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return Notification.objects.filter(to_user_id=request.user.id)

    # def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
    #     if change:
    #         obj.viewed_state = True
    #         obj.save()
            # super(NotificationAdmin, self).save_model(request, obj, context['adminform'].form, change)
        # super().render_change_form(request, context, add, change, form_url, obj)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    pass

