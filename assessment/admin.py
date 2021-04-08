from django.contrib import admin

# Register your models here.
from django.utils.html import format_html

from assessment.models import AssessmentCategory
from manager.admin import BaseModelAdmin


# @admin.register(AssessmentCategory)
class ClassRoomAdmin(BaseModelAdmin):
    list_display = ("id", "get_code", "content", "type")
    search_fields = ['content', 'code', 'type']
    readonly_fields = ['created_user', 'updated_user']

    def get_code(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.code)

    get_code.short_description = "Mã đánh giá"
    get_code.admin_order_field = "code"

    pass
