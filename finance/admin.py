from datetime import datetime, timedelta

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.forms import BaseInlineFormSet
from django.utils.html import format_html
from django.utils.translation import gettext as _

from app_config.settings import DEFAULT_DATE_FORMAT
from finance.forms import StudentDebtForm
from finance.models import StudentDebt, Revenue, Payment, StudentSendPaymentRequest, StudentDebtView, Reward
from finance.views import apply_student_debt
from manager.admin import BaseModelAdmin, BaseTabularInline
from manager.constant import CHOICE_EMPTY, GROUP
from manager.utils import currency, custom_titled_filter
from message.views import send_inform_has_new_payment_request
from user.models import Student, BusinessEmployee


class PaymentInlineFormSet(BaseInlineFormSet):
    def clean(self):
        if self.is_valid():
            super(PaymentInlineFormSet, self).clean()

            student_debt = self.instance
            must_pay_amount = (1 - student_debt.discount_percent / 100) * student_debt.origin_amount
            sum_paid_amount = 0
            for form in self.forms:
                if form.is_valid():
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        sum_paid_amount += form.cleaned_data['paid_amount']

            if sum_paid_amount and 0 < must_pay_amount < sum_paid_amount:
                raise ValidationError('Tổng số tiền các lần nộp vượt quá tổng số tiền phải nộp.')

            # Tính lại số tiền còn nợ
            self.instance.rest_amount = must_pay_amount - sum_paid_amount


class PaymentInline(BaseTabularInline):
    model = Payment
    fields = ('paid_amount', 'payment_method', 'completed_pay_date')
    formset = PaymentInlineFormSet


@admin.register(StudentDebt)
class StudentDebtAdmin(BaseModelAdmin):
    list_display = ("id", "title_link", 'course', "get_student_name", "get_student_code", "get_student_email"
                    , "get_student_phone", "get_origin_amount", "get_paid_amount_total", "get_rest_amount", "reward"
                    , "contract_state", "print_receipt", "print_contract")
    list_filter = (("student__user__full_name", custom_titled_filter('Tên HV')),
                   ("student__user__phone", custom_titled_filter('SĐT HV')),("rest_amount", custom_titled_filter('Còn Nợ')))
    search_fields = ("title",
                     "course__code", "course__name",
                     "student__user__full_name", "student__user__phone", "student__user__email"
                     )
    fields = ('course', 'study_schedule_select', 'student', 'student_level', 'origin_amount',
              'reward',
              'rest_amount', 'back_amount', 'back_reason', 'plan_date', 'completed_pay_date', 'gift',
              'collector', 'counselor',
              'consultant', 'title', 'contract', 'receipt', 'contract_state', 'created_user', 'updated_user')
    readonly_fields = ('reward', 'rest_amount', 'collector', 'created_user', 'updated_user', 'contract', 'receipt')
    inlines = [PaymentInline]
    form = StudentDebtForm

    def get_student_name(self, obj):
        return obj.student.user.full_name

    get_student_name.short_description = 'Họ và tên'
    get_student_name.admin_order_field = 'student__user__full_name'

    def get_origin_amount(self, obj):
        return currency(obj.origin_amount)

    get_origin_amount.short_description = 'Giá'
    get_origin_amount.admin_order_field = 'origin_amount'

    def get_paid_amount_total(self, obj):
        paid_amount = Payment.objects.filter(student_debt=obj).aggregate(Sum('paid_amount'))['paid_amount__sum']
        if not paid_amount:
            paid_amount = 0
        return currency(paid_amount)

    get_paid_amount_total.short_description = 'Đã thanh toán'

    # get_paid_amount_total.admin_order_field = 'paid_amount'

    def get_rest_amount(self, obj):
        return currency(obj.rest_amount)

    get_rest_amount.short_description = 'Còn nợ'
    get_rest_amount.admin_order_field = 'rest_amount'

    def get_student_code(self, obj):
        return obj.student.user.user_code

    get_student_code.short_description = 'Mã HV'
    get_student_code.admin_order_field = 'student__user__user_code'

    def get_student_email(self, obj):
        return obj.student.user.email

    get_student_email.short_description = 'Email'
    get_student_email.admin_order_field = 'Email'

    def get_student_phone(self, obj):
        return obj.student.user.phone

    get_student_phone.short_description = 'Số ĐT'
    get_student_phone.admin_order_field = 'student__user__phone'

    def print_receipt(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url_display}</a>",
                           url='/admin/student/receipt?student_debt_id=' + str(obj.id), url_display="Xem")

    print_receipt.short_description = "Hóa đơn"

    def print_contract(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url_display}</a>",
                           url='/admin/student/contract?student_debt_id=' + str(obj.id), url_display="Xem")

    print_contract.short_description = "Hợp đồng"

    def get_state(self, obj):
        must_amount = obj.origin_amount * (1 - obj.discount_percent / 100)
        total_paid_amount = Payment.objects.filter(student_debt=obj).aggregate(Sum('paid_amount'))['paid_amount__sum']
        if not total_paid_amount or (must_amount > total_paid_amount):
            return "Chưa hoàn thành"
        return "Đã hoàn thành"

    get_state.short_description = "Trạng thái"
    get_state.admin_order_field = "origin_amount"

    def title_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.title)

    # def get_payed_date(self, obj):
    #     return date_format(obj.completed_pay_date, DEFAULT_DATE_FORMAT)

    title_link.short_description = _('Nội dung')
    # get_payed_date.short_description = _('Ngày trả')
    # get_payed_date.admin_order_field = 'payed_date'
    title_link.admin_order_field = 'title'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return StudentDebt.objects.filter(student__user__centre__id=request.user.centre.id)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        fields = context['adminform'].form.fields
        if 'student' in fields:
            context['adminform'].form.fields['student'].choices = CHOICE_EMPTY
            choices = Student.objects.all()\
                .annotate(user_label=Concat('user__full_name', V(' ('), 'user__user_code', V(')')))\
                .values_list('id', 'user_label')
            if choices.count() > 0:
                context['adminform'].form.fields['student'].choices = CHOICE_EMPTY + list(choices)

        if 'collector' in fields:
            # context['adminform'].form.fields['collector'].choices = CHOICE_EMPTY
            # choices = Receptionist.objects.filter(user=request.user) \
            #     .annotate(user_label=Concat('user__full_name', V(' ('), 'user__user_code', V(')'))) \
            #     .values_list('id', 'user_label')
            # if choices.count() > 0:
            #     context['adminform'].form.fields['collector'].choices = list(choices)
            context['adminform'].form.fields['collector'] = request.user

        if 'counselor' in fields:
            context['adminform'].form.fields['counselor'].choices = CHOICE_EMPTY
            choices = BusinessEmployee.objects.all() \
                .annotate(user_label=Concat('user__full_name', V(' ('), 'user__user_code', V(')'))) \
                .values_list('id', 'user_label')
            if choices.count() > 0:
                context['adminform'].form.fields['counselor'].choices = CHOICE_EMPTY + list(choices)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj and obj.pk:
            readonly_fields += ("course", "study_schedule_select", "origin_amount", "student")
        return readonly_fields

    def save_model(self, request, obj, form, change):
        # In case create new student debt
        if not change:
            obj.collector = request.user
            super(StudentDebtAdmin, self).save_model(request, obj, form, change)
            # lấy khóa học được đk
            course = form.cleaned_data['course']
            apply_student_debt(student_debt=obj, course=course, owner=request.user)
            # obj.contract = format_html("<a class='btn btn-primary' target='_blank' href='{url}'>{url_display}</a>",
            #                            url='/admin/student/contract?student_debt_id=' + str(obj.pk), url_display='Xem')
            # obj.receipt = format_html("<a class='btn btn-success' target='_blank' href='{url}'>{url_display}</a>",
            #                           url='/admin/student/receipt?student_debt_id=' + str(obj.pk), url_display='Xem')
            # # lấy khóa học được đk
            # course = form.cleaned_data['course']
            #
            # # Add sv vào lớp chờ của khóa tương ứng. Nếu là khóa combo => add vào lớp chờ của khóa đầu tiên
            # course_code = course.code
            # course_code_array = course_code.split('_')
            #
            # # Truong hop khoa don le
            # course_id = course.id
            #
            # next_next_course_code = None
            # # Trường hợp là khóa combo
            # if len(course_code_array) > 1:
            #     course_id = Course.objects.get(code=course_code_array[0]).id
            #     # Get khóa tiếp theo nữa của sv này
            #     next_next_course_code = course_code_array[1]
            #
            # waiting_classes = Classes.objects.get(course=course_id, centre=obj.student.user.centre, waiting_flag=True)
            # class_student = ClassesStudents(classes=waiting_classes,
            #                                 student=obj.student, student_debt=obj,
            #                                 next_course_code=next_next_course_code,
            #                                 updated_user=request.user, created_user=request.user)
            # # add student into watting class of course
            # class_student.save()
        else:
            super(StudentDebtAdmin, self).save_model(request, obj, form, change)

    pass


# @admin.register(StudentDebtView)
class StudentDebtViewAdmin(BaseModelAdmin):
    list_display = ("get_id", "get_title", 'get_course'
                    , "get_student_name", "get_student_code", "get_student_email"
                    , "get_student_phone", "get_origin_amount", "get_paid_amount_total"
                    , "get_rest_amount", "get_plan_date")
    # list_filter = (("student__user__full_name", custom_titled_filter('Tên HV')),
    #                ("student__user__phone", custom_titled_filter('SĐT HV')))
    # search_fields = ("student__user__full_name", "student__user__phone", "student__user__email",)
    list_display_links = None

    def get_student_name(self, obj):
        return obj.student.user.full_name

    get_student_name.short_description = 'Họ và tên'
    get_student_name.admin_order_field = 'student__user__full_name'

    def get_origin_amount(self, obj):
        return currency(obj.origin_amount)

    get_origin_amount.short_description = 'Giá gốc'
    get_origin_amount.admin_order_field = 'origin_amount'

    def get_paid_amount_total(self, obj):
        paid_amount = Payment.objects.filter(student_debt=obj).aggregate(Sum('paid_amount'))['paid_amount__sum']
        if not paid_amount:
            paid_amount = 0
        return currency(paid_amount)

    get_paid_amount_total.short_description = 'Đã thanh toán'

    # get_paid_amount_total.admin_order_field = 'paid_amount'

    def get_rest_amount(self, obj):
        return currency(obj.rest_amount)

    get_rest_amount.short_description = 'Còn nợ'
    get_rest_amount.admin_order_field = 'rest_amount'

    def get_student_code(self, obj):
        return obj.student.user.user_code

    get_student_code.short_description = 'Mã HV'
    get_student_code.admin_order_field = 'student__user__user_code'

    def get_student_email(self, obj):
        return obj.student.user.email

    get_student_email.short_description = 'Email'
    get_student_email.admin_order_field = 'Email'

    def get_student_phone(self, obj):
        return obj.student.user.phone

    get_student_phone.short_description = 'Số ĐT'
    get_student_phone.admin_order_field = 'student__user__phone'

    def get_id(self, obj):
        return obj.id
    get_id.short_description = "ID"

    def get_title(self, obj):
        return obj.title
    get_title.short_description = "Tiêu đề"

    def get_course(self, obj):
        return obj.course
    get_course.short_description = "Khóa học"

    def get_plan_date(self, obj):
        return obj.plan_date.strftime(DEFAULT_DATE_FORMAT)
    get_plan_date.short_description = "Ngày hẹn thanh toán"

    def get_queryset(self, request):
        next_seven_date = datetime.now() + timedelta(days=7)
        return StudentDebt.objects.filter(plan_date__lte=next_seven_date, rest_amount__gt=0)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StudentSendPaymentRequest)
class StudentSendPaymentRequestAdmin(BaseModelAdmin):
    list_display = ("id", "title_link", 'full_name', "email", "phone", "course", "classes",
                    "study_schedule_select", "get_paid_amount", "payment_method", "transaction_id",
                    "reward", "get_send_date", "print_receipt", "get_state")

    student_list_display = ("id", "title_link", 'full_name', "email", "phone", "course",
                          "study_schedule_select", "get_paid_amount", "payment_method", "transaction_id",
                            "reward", "get_send_date", "print_receipt", "get_student_state")
    search_fields = ("title",
                     "course__code", "course__name", "classes__name", "classes__code",
                     "full_name", "phone", "email", "transaction_id")
    list_filter = ("state", "send_date",)
    fields = ("title", "course", "paid_amount", "transaction_id", "payment_method", "reward", "send_date", "state")

    readonly_fields = ("state", "reward",)

    def print_receipt(self, obj):
        if obj.state == 1:
            student_debt = obj.student_debt
            if not student_debt:
                student_debts = StudentDebt.objects.filter(
                    centre=obj.centre, course=obj.course,
                    student__user__email=obj.email)
                if student_debts.count() > 0:
                    student_debt = student_debts[0]
            if student_debt:
                return format_html("<a href='{url}' target='_blank'>{url_display}</a>",
                                   url='/admin/student/receipt?req_pay_id=' + str(obj.id), url_display="Xem")
        return None

    print_receipt.short_description = "Phiếu thu"

    def title_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.title)
    title_link.short_description = "Tiêu đề"
    title_link.admin_order_field = "title"

    def get_send_date(self, obj):
        return obj.send_date.strftime(DEFAULT_DATE_FORMAT)
    get_send_date.short_description = "Ngày nộp"
    get_send_date.admin_order_field = "send_date"

    def get_paid_amount(self, obj):
        return currency(obj.paid_amount)
    get_paid_amount.short_description = "Số tiền nộp"
    get_paid_amount.admin_order_field = "paid_amount"

    def get_student_state(self, obj):
        if not obj.state:
            return "Chờ duyệt"
        if obj.state == 1:
            return "Đồng ý"
        if obj.state == 2:
            return "Chờ HV"
        return "Từ chối"

    get_student_state.short_description = "Trạng thái"
    get_student_state.admin_order_field = "state"

    def get_state(self, obj):
        if not obj.state:
            html_content = '<button type="button" onclick="return' \
                           ' changePaymentRequestState($(this), ' + str(obj.id) + ', 1'\
                           + ')" class="btn btn-primary m-1" title="Đồng ý thông tin thanh toán. Cập nhật thông tin HV và thông tin thanh toán vào cơ sở dữ liệu.">' \
                           '<i class="fas fa-check"></i></button>' \
                           '<button type="button" onclick="return' \
                             ' changePaymentRequestState($(this), ' + str(obj.id) + ', 2' \
                           + ')" class="btn btn-success m-1" title="Gửi thông báo qua email tới học viên do dữ liệu đăng ký không chính xác">' \
                           '<i class="fas fa-paper-plane"></i></button>' \
                           '<button type="button" onclick="return' \
                             ' changePaymentRequestState($(this), ' + str(obj.id) + ', 3'\
                           + ')" class="btn btn-danger m-1" title="Huỷ nội dung thanh toán.">' \
                           '<i class="far fa-trash-alt"></i></button>'
            return format_html(html_content)
        if obj.state == 1:
            return "Đồng ý"
        if obj.state == 2:
            return "Chờ HV"
        return "Từ chối"

    get_state.short_description = "Trạng thái"
    get_state.admin_order_field = "state"

    def get_list_display(self, request):
        if request.user.is_superuser or request.user.groups.id == GROUP.RECEPTIONIST:
            return self.list_display
        return self.student_list_display

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        if request.user.groups.id == GROUP.RECEPTIONIST:
            return StudentSendPaymentRequest.objects.filter(centre=request.user.centre)
        # Truong hop user login la sinh vien
        return StudentSendPaymentRequest.objects.filter(email=request.user.email)

    def save_model(self, request, obj, form, change):
        user = request.user
        obj.email = user.email
        obj.phone = user.phone
        obj.address = user.address
        obj.full_name = user.full_name
        obj.centre = request.user.centre
        super(StudentSendPaymentRequestAdmin, self).save_model(request, obj, form, change)

        # Gửi email và notify tới lễ tân của trung tâm và admin
        send_inform_has_new_payment_request(req_pay=obj)


    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        fields = context['adminform'].form.fields
        if not change and request.user.groups.id == GROUP.STUDENT:
            if 'full_name' in fields:
                context['adminform'].form.fields['full_name'].initial = request.user.full_name

            if 'email' in fields:
                context['adminform'].form.fields['email'].initial = request.user.email

            if 'phone' in fields:
                context['adminform'].form.fields['phone'].initial = request.user.phone

            if 'address' in fields:
                context['adminform'].form.fields['address'].initial = request.user.address

        return super().render_change_form(request, context, add, change, form_url, obj)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser \
               or request.user.groups.id == GROUP.STUDENT \
               or request.user.groups.id == GROUP.RECEPTIONIST \
               or request.user.groups.id == GROUP.CENTRE_ADMIN

    def has_add_permission(self, request):
        # Chỉ sv mới đc phép nộp tiền
        return request.user.groups and request.user.groups.id == GROUP.STUDENT

    def has_change_permission(self, request, obj=None):
        return False
    pass


@admin.register(Reward)
class RewardAdmin(BaseModelAdmin):
    list_display = ("id", "title_link", "code", "type", "quantity", "get_courses", "discount_percent", "gift", "get_start_date", "get_end_date")

    def title_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>", url=str(obj.id) + '/change', url_display=obj.title)

    title_link.short_description = _('Tiêu đề')
    title_link.admin_order_field = 'title'

    def get_courses(self, obj):
        course_codes = obj.course.values_list('code', flat=True)
        if course_codes:
            content = ""
            for c in course_codes:
                content += c + "<br>"
            return format_html(content)
        return "Tất cả khoá học"

    get_courses.short_description = _('Khóa học')
    get_courses.admin_order_field = 'course'

    def get_start_date(self, obj):
        return obj.start_date.strftime(DEFAULT_DATE_FORMAT)
    get_start_date.short_description = "Ngày bắt đầu"
    get_start_date.admin_order_field = "start_date"

    def get_end_date(self, obj):
        return obj.end_date.strftime(DEFAULT_DATE_FORMAT)
    get_end_date.short_description = "Ngày kết thúc"
    get_end_date.admin_order_field = "end_date"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser


# @admin.register(StudentReceiveReward)
# class StudentReceiveRewardAdmin(BaseModelAdmin):
#     # list_display = ("id", "student__user__user_code", "student__user__full_name", "reward__title", "reward__code",
#     #                 "reward__type", "reward__discount_percent")
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         return False
#
#     def has_add_permission(self, request, obj=None):
#         return False
#     pass


@admin.register(Revenue)
class RevenueAdmin(BaseModelAdmin):
    change_list_template = "admin/index.html"
    # list_display = ("id", "title_link", "centre", "user", "get_amount", "input_date", "note")
    # icon_name = 'money'
    #
    # list_filter = ("centre", ('input_date', DateRangeFilter),)
    # readonly_fields = ['created_user', 'updated_user']
    #
    # def title_link(self, obj):
    #     return format_html("<a href='{url}'>{url_display}</a>", url=str(obj.id) + '/change', url_display=obj.title)
    #
    # def get_amount(self, obj):
    #     return currency(obj.amount)
    #
    # title_link.short_description = _('Tiêu đề')
    # get_amount.short_description = _('Số tiền (VNĐ)')
    # get_amount.admin_order_field = 'amount'
    # title_link.admin_order_field = 'title'
    #
    # def get_queryset(self, request):
    #     if request.user.is_superuser:
    #         return super(BaseModelAdmin, self).get_queryset(request)
    #     return Revenue.objects.filter(centre__id=request.user.centre.id)
    #
    # pass
