from datetime import datetime

from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.auth import hashers
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import gettext as _

from app_config.settings import DEFAULT_DATE_FORMAT
from centre.admin import add_student_to_study_shift
from centre.models import ClassesStudents, ClassesTeachers, StudyShiftStudent, Classes, Issues
from finance.models import StudentDebt
from manager.admin import BaseModelAdmin, BaseTabularInline, BaseStackedInline
from manager.constant import GROUP
from manager.utils import get_random_string, date_format, custom_titled_filter, str_to_int, \
    get_parent_object_from_request
from message.views import send_email_create_user_success
from user.models import Student, Teacher, Receptionist, StudentCare, AuthUser, Commendation, Tests, StudentTestResult, \
    CommendationStudent, BusinessEmployee


class TestResultInline(BaseTabularInline):
    model = StudentTestResult
    can_delete = True
    verbose_name_plural = 'Kết quả'

    fields = ('student', 'point', 'note')

    def get_course(self, obj):
        return obj.test.classes.course.name

    get_course.short_description = _('Khóa học')
    get_course.admin_order_field = 'test__classes__course__name'

    def get_classes(self, obj):
        return obj.test.classes.name

    get_classes.short_description = _('Lớp học')
    get_classes.admin_order_field = 'test__classes__name'


class StudentDebtAdminInline(BaseTabularInline):
    # can_print_receipt = True
    model = StudentDebt
    verbose_name = "Công nợ"
    verbose_name_plural = "Công nợ"
    # fields = ("contract", "receipt",)
    readonly_fields = ("contract", "receipt",)

    # def get_contract_link(self, obj):
    #     return format_html("<a class='btn btn-primary' target='_blank' href='{url}'>{url_display}</a>",
    #                        url='/admin/student/contract?student_debt_id=' + str(obj.contract), url_display='Xem')
    #
    # get_contract_link.short_description = 'Hợp đồng'
    #
    # def get_receipt_link(self, obj):
    #     return format_html("<a class='btn btn-basic' target='_blank' href='{url}'>{url_display}</a>",
    #                        url='/admin/student/receipt?student_debt_id=' + str(obj.receipt), url_display='Xem')
    # get_receipt_link.short_description = 'Hóa đơn'

    # def get_formset(self, request, obj=None, **kwargs):
    #     form_set = super(BaseTabularInline, self).get_formset(request, obj, **kwargs)
    #     if obj:
    #         form_set.can_print_receipt = True
    #         form_set.print_receipt_link = '/admin/student/receipt?student_debt_id=' + str(obj.id)
    #     else:
    #         form_set.can_print_receipt = False
    #         form_set.print_receipt_link = '#'
    #     return form_set


class UserStudentAdminInline(BaseStackedInline):
    extra = 1
    model = Student
    verbose_name = "TT sinh viên"
    verbose_name_plural = "TT sinh viên"
    fk_name = "user"
    readonly_fields = ('created_user', 'updated_user',)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuthUser)
class UserAdmin(BaseModelAdmin):
    icon_name = 'person'
    list_display = ("id", "username_link", "full_name", "email", "phone", "groups", "is_active")
    search_fields = ['username', 'full_name', 'user_code', 'email', "phone"]
    fields = ("centre", "full_name", "username", "email", "phone", "birth_day",
              "address", "date_joined", "is_active", "groups")
    change_readonly_fields = ("username", "date_joined", 'user_code',"groups")
    student_inlines = [UserStudentAdminInline]
    inlines = []
    actions = ['lock_users', 'unlock_users']

    # change_list_template = 'admin/change_list.html'

    def username_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>", url=str(obj.id) + '/change', url_display=obj.username)

    username_link.short_description = _('username')
    username_link.admin_order_field = 'username'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.change_readonly_fields
        return []

    def get_inlines(self, request, obj):
        if not obj or obj.groups_id == GROUP.STUDENT:
            return self.student_inlines
        return self.inlines

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            random_password = get_random_string(8)
            obj.password = hashers.make_password(password=random_password)

            # In case user login is not super admin => add new user into the same centre to centre of user login.
            if not request.user.is_superuser:
                obj.centre = request.user.centre

            super(UserAdmin, self).save_model(request, obj, form, change)
            # In case create student
            if obj.groups_id == GROUP.STUDENT:
                rd = request.POST
                student = Student.objects.create(
                    user=obj, state=str_to_int(rd['student_user_info_set-0-state']),
                    academic_power=str_to_int(rd['student_user_info_set-0-academic_power']),
                    parents_phone=rd['student_user_info_set-0-parents_phone'],
                    current_company=rd['student_user_info_set-0-current_company'],
                    branch=rd['student_user_info_set-0-branch'],
                    school_year=rd['student_user_info_set-0-school_year'],
                    learning_target=rd['student_user_info_set-0-learning_target'],
                    learning_purpose=rd['student_user_info_set-0-learning_purpose'],
                    free_to_test=rd['student_user_info_set-0-free_to_test'],
                    free_to_learn=rd['student_user_info_set-0-free_to_learn'],
                    how_to_know_odin=rd['student_user_info_set-0-how_to_know_odin'],
                    created_user=request.user, updated_user=request.user
                )
                obj.user_code = "PP" + str(student.id).zfill(6)
            # In case create teacher
            if obj.groups_id == GROUP.TEACHER:
                teacher = Teacher.objects.create(user=obj, created_user=request.user, updated_user=request.user)
                obj.user_code = "PP" + str(teacher.id).zfill(6)
            # In case create receptionist
            elif obj.groups_id == GROUP.RECEPTIONIST:
                receptions = Receptionist.objects.create(user=obj, created_user=request.user,
                                                         updated_user=request.user)
                obj.user_code = "PP" + str(receptions.id).zfill(6)
            # In case create student care
            elif obj.groups_id == GROUP.STUDENT_CARE:
                student_care = StudentCare.objects.create(user=obj, created_user=request.user,
                                                          updated_user=request.user)
                obj.user_code = "PP" + str(student_care.id).zfill(6)

            # In case create business
            elif obj.groups_id == GROUP.BUSINESS:
                business_employee = BusinessEmployee.objects.create(user=obj, created_user=request.user,
                                                          updated_user=request.user)
                obj.user_code = "PP" + str(business_employee.id).zfill(6)
            super(UserAdmin, self).save_model(request, obj, form, change)
            send_email_create_user_success(to_user=obj,
                                           password=random_password,
                                           login_url=request.META['HTTP_HOST'] + ':' + '/admin/login')
        else:
            super(UserAdmin, self).save_model(request, obj, form, change)
            # send_email_update_user(to_name=obj.full_name, to_username=obj.username, to_address=obj.email)

    def save_related(self, request, form, formsets, change):
        super(UserAdmin, self).save_related(request, form, formsets, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return AuthUser.objects.filter(centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = ('groups', 'is_active')
        if request.user.is_superuser:
            filters = ("centre",) + filters

        return filters

    def lock_users(self, request, queryset):
        queryset.filter(is_superuser=False).update(is_active=False)
    lock_users.short_description = "Khóa người dùng (không bao gồm admin)"

    def unlock_users(self, request, queryset):
        queryset.update(is_active=True)

    unlock_users.short_description = "Mở khóa người dùng"

    def get_actions(self, request):
        actions = super(UserAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            del actions['lock_users']
            del actions['unlock_users']
        return actions

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    pass


# class ClassesStudentsInlineFormSet(BaseInlineFormSet):
#
#     def get_queryset(self):
#         qs = super(ClassesStudentsInlineFormSet, self).get_queryset()
#         return qs.filter(state=)

class ClassesStudentsInline(BaseTabularInline):
    extra = 0
    model = ClassesStudents
    # can_delete = True
    fields = ('classes', "state", 'assessment', 'note')
    # readonly_fields = ('classes__state',)
    verbose_name = "Lớp học"
    verbose_name_plural = "Lớp học"

    # def classes__state(self, obj):
    #     return obj.classes.state
    # classes__state.short_description = _('Mã lớp')
    #
    # def get_classes_name(self, obj):
    #     return obj.classes.name
    # get_classes_name.short_description = _('Tên lớp')

    def get_queryset(self, request):
        query = super(ClassesStudentsInline, self).get_queryset(request)
        # ẩn những lớp mà sv này hủy
        query = query.filter(~Q(state=7))
        return query

    def has_delete_permission(self, request, obj=None):
        return False


class CommendationStudentInline(BaseTabularInline):
    model = CommendationStudent
    # fields = ('code', 'title', 'centre')
    # fields = ('study_shift', 'student', 'attendance', 'leave_request', 'assessment', 'home_work', 'note')


# For parent is student
class StudyShiftStudentInline(BaseTabularInline):
    extra = 0
    model = StudyShiftStudent
    fields = ('study_shift', 'student', 'attendance', 'leave_request', 'assessment', 'home_work', 'note')

    def get_queryset(self, request):
        # Chỉ hiện thị ds buổi học của những lớp học mà sinh viên tham gia.
        student = get_parent_object_from_request(self, request)
        student_ids = ClassesStudents.objects.filter(student=student).values_list("student__id", flat=True)
        return StudyShiftStudent.objects.filter(student__id__in=student_ids)


class ClassesStudentFilter(SimpleListFilter):
    title = 'Lớp học' # or use _('country') for translated title
    parameter_name = 'Classes'

    def lookups(self, request, model_admin):
        # countries = set([c.country for c in Classes.objects.all()])
        # return [(c.id, c.name) for c in countries]
        # You can also use hardcoded model name like "Country" instead of
        # "model_admin.model" if this is not direct foreign key filter
        if request.user.is_superuser:
            return Classes.objects.all().values_list('id', 'name')
        return Classes.objects.filter(centre=request.user.centre).values_list('id', 'name')

    def queryset(self, request, queryset):
        if self.value():
            cls_students = ClassesStudents.objects.filter(classes_id=self.value()).values_list('student_id')
            return queryset.filter(id__in=cls_students)
        else:
            return queryset


class StudentCallHistoryInline(BaseTabularInline):
    model = Issues
    verbose_name = "Lịch sử gọi"
    verbose_name_plural = "Lịch sử gọi"

    def get_field_queryset(self, db, db_field, request):
        if db_field.column == 'call_user_id':
            return StudentCare.objects.all()


@admin.register(Student)
class StudentAdmin(BaseModelAdmin):

    list_display = ("id", "student_code_link", "student_name", "get_phone", "get_email", "academic_power",
                    "get_register_course", "count_study_shift", "state")
    # list_display_links = ("state",)
    search_fields = ['user__username', 'user__full_name',
                     'user__user_code', 'user__email', "user__phone"]
    readonly_fields = ['user', 'created_user', 'updated_user']
    inlines = [
        ClassesStudentsInline,
        StudentDebtAdminInline,
        StudyShiftStudentInline,
        CommendationStudentInline,
        TestResultInline,
        StudentCallHistoryInline
    ]

    def get_register_course(self, obj):
        # return 1
        query = StudentDebt.objects.filter(student=obj).values_list('course__code', flat=True)
        content = ""
        for q in query:
            content = content + "<p>" + q + "</p>"
        return format_html(content)
    get_register_course.short_description = "Khoá học"

    def count_study_shift(self, obj):
        return StudyShiftStudent.objects.filter(student=obj, attendance=True).count()
    count_study_shift.short_description = "Số buổi đã học"

    def has_add_permission(self, request):
        return False

    def student_code_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.user.user_code)

    student_code_link.short_description = _('Mã học viên')
    student_code_link.admin_order_field = 'user__user_code'

    def get_birth_day(self, obj):
        return date_format(obj.user.birth_day, DEFAULT_DATE_FORMAT)

    get_birth_day.short_description = _('Ngày sinh')
    get_birth_day.admin_order_field = 'user__birth_day'

    def get_phone(self, obj):
        return obj.user.phone

    get_phone.short_description = _('Số điện thoại')
    get_phone.admin_order_field = 'user__phone'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = _('Email')
    get_email.admin_order_field = 'user__email'

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = _('username')
    get_username.admin_order_field = 'user__username'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return Student.objects.filter(user__centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = ("state", "academic_power", ClassesStudentFilter)
        if request.user.is_superuser:
            filters = ("user__centre", "state", "academic_power", ClassesStudentFilter)
        return filters

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # context['adminform'].form.fields['user'].widget.can_view_related = True
        # context['adminform'].form.fields['user'].widget.can_add_related = False
        # context['adminform'].form.fields['user'].widget.can_change_related = False
        # context['adminform'].form.fields['user'].widget.can_delete_related = False
        # context['adminform'].form.fields['user'].choices = CHOICE_EMPTY
        # choices = AuthUser.objects.filter(groups_id=GROUP.STUDENT).values_list('id', 'username')
        # if choices.count() > 0:
        #     context['adminform'].form.fields['user'].choices = CHOICE_EMPTY + list(choices)
        #
        # if obj:
        #     context['adminform'].form.fields['created_user'].choices = ((request.user.id, request.user),)
        #     context['adminform'].form.fields['created_user'].widget.attrs['disabled'] = 'disabled'
        #     context['adminform'].form.fields['updated_user'].choices = ((request.user.id, request.user),)
        return super().render_change_form(request, context, add, change, form_url, obj)

    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['created_user', 'updated_user']
    #     if not obj or not obj.pk:
    #         readonly_fields = ['created_user', 'updated_user']
    #     return readonly_fields

    def save_model(self, request, obj, form, change):
        super(StudentAdmin, self).save_model(request, obj, form, change)
        # register_courses = form.cleaned_data['classes']

    def save_related(self, request, form, formsets, change):
        super(StudentAdmin, self).save_related(request, form, formsets, change)

        obj = form.instance
        # Get ds lớp học chứa sinh viên này
        cls_students = ClassesStudents.objects.filter(student_id=obj.id)

        # Kiem tra xem sinh vien dang o lop va chuan hoan thanh
        count_not_complete_classes = 0
        for cls_student in cls_students:
            # Neu trang thai la nhận lớp => add sinh vieen vao cac buoi hoc chua dien ra
            if cls_student.state == 2:
                count_not_complete_classes += 1
                add_student_to_study_shift(cls_student)
            # Neu trang thai la huy
            elif cls_student.state == 7:
                # Can xoa nhung buoi hoc chua dien ra cua sinh vien o lop nay
                ss_shifts = StudyShiftStudent.objects.filter(student=cls_student.student, study_shift__classes=cls_student.classes)
                for ss_student in ss_shifts:
                    sys_date_time = datetime.today()
                    from_date_time = datetime.combine(ss_student.study_shift.session_date, ss_student.study_shift.from_time)
                    # Nếu buổi học chưa diễn ra
                    if sys_date_time < from_date_time:
                        ss_student.delete()

        if count_not_complete_classes > 1:
            messages.warning(request=request, message="Sinh viên được thêm vào nhiều lớp. "
                                                      "Sinh viên được tham gia lớp tiếp theo nếu hoàn thành lớp học hiện tại.")

    pass


class ClassesTeachersInline(BaseTabularInline):
    model = ClassesTeachers
    # can_delete = True
    fields = ('classes', 'assessment', 'note')
    # readonly_fields = ('classes__state',)
    verbose_name = "Lớp học"
    verbose_name_plural = "Lớp học"


@admin.register(Teacher)
class TeacherAdmin(BaseModelAdmin):
    list_display = ("id", "teacher_code_link", "teacher_name", "centre",
                    "get_username", "get_email", "get_birth_day", "get_phone", "get_date_joined", "get_address")
    inlines = [ClassesTeachersInline, ]
    search_fields = ['user__username', 'user__full_name',
                     'user__user_code', 'user__email', "user__phone"]
    readonly_fields = ['user', 'created_user', 'updated_user']

    def teacher_code_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.user.user_code)

    teacher_code_link.short_description = "Mã giáo viên"
    teacher_code_link.admin_order_field = 'user__user_code'

    def get_birth_day(self, obj):
        return obj.user.birth_day.strftime(DEFAULT_DATE_FORMAT)

    get_birth_day.short_description = _('Ngày sinh')
    get_birth_day.admin_order_field = 'user__birth_day'

    def get_phone(self, obj):
        return obj.user.phone

    get_phone.short_description = _('Số điện thoại')
    get_phone.admin_order_field = 'user__phone'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = _('Email')
    get_email.admin_order_field = 'user__email'

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = _('username')
    get_username.admin_order_field = 'user__username'

    def get_address(self, obj):
        return obj.user.address

    get_address.short_description = _('address')
    get_address.admin_order_field = 'user__address'

    def get_date_joined(self, obj):
        return date_format(obj.user.date_joined, DEFAULT_DATE_FORMAT)

    get_date_joined.short_description = _('Ngày tham gia')
    get_date_joined.admin_order_field = 'user__date_joined'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return Teacher.objects.filter(user__centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = self.list_filter
        if request.user.is_superuser:
            filters = ("user__centre",)
        return filters

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # context['adminform'].form.fields['user'].choices = CHOICE_EMPTY
        # choices = AuthUser.objects.filter(groups_id=GROUP.TEACHER).values_list('id', 'username')
        # if choices.count() > 0:
        #     context['adminform'].form.fields['user'].choices = CHOICE_EMPTY + list(choices)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def has_add_permission(self, request):
        return False
    pass


@admin.register(Receptionist)
class ReceptionistAdmin(BaseModelAdmin):
    list_display = ("id", "reception_code_link", "reception_name", "centre",
                    "get_username", "get_email", "get_birth_day",
                    "get_phone", "get_date_joined", "get_address")
    search_fields = ['user__username', 'user__full_name',
                     'user__user_code', 'user__email', "user__phone"]
    readonly_fields = ['user', 'created_user', 'updated_user']

    def reception_code_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.user.user_code)

    reception_code_link.short_description = "Mã nhân viên"
    reception_code_link.admin_order_field = 'user__user_code'

    def get_birth_day(self, obj):
        return obj.user.birth_day.strftime(DEFAULT_DATE_FORMAT)

    get_birth_day.short_description = _('Ngày sinh')
    get_birth_day.admin_order_field = 'user__birth_day'

    def get_phone(self, obj):
        return obj.user.phone

    get_phone.short_description = _('Số điện thoại')
    get_phone.admin_order_field = 'user__phone'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = _('Email')
    get_email.admin_order_field = 'user__email'

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = _('username')
    get_username.admin_order_field = 'user__username'

    def get_address(self, obj):
        return obj.user.address

    get_address.short_description = _('address')
    get_address.admin_order_field = 'user__address'

    def get_date_joined(self, obj):
        return date_format(obj.user.date_joined, DEFAULT_DATE_FORMAT)

    get_date_joined.short_description = _('Ngày tham gia')
    get_date_joined.admin_order_field = 'user__date_joined'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return Receptionist.objects.filter(user__centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = self.list_filter
        if request.user.is_superuser:
            filters = ("user__centre",)
        return filters

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # context['adminform'].form.fields['user'].choices = CHOICE_EMPTY
        # choices = AuthUser.objects.filter(groups_id=GROUP.RECEPTIONIST).values_list('id', 'username')
        # if choices.count() > 0:
        #     context['adminform'].form.fields['user'].choices = CHOICE_EMPTY + list(choices)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def has_add_permission(self, request):
        return False
    pass


@admin.register(StudentCare)
class StudentCareAdmin(BaseModelAdmin):
    list_display = ("id", "student_care_code_link", "student_care_name", "centre",
                    "get_username", "get_email", "get_birth_day",
                    "get_phone", "get_date_joined", "get_address")
    search_fields = ['user__username', 'user__full_name',
                     'user__user_code', 'user__email', "user__phone"]
    readonly_fields = ['user', 'get_username', 'get_email', 'created_user', 'updated_user']

    def student_care_code_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.user.user_code)

    student_care_code_link.short_description = "Mã nhân viên"
    student_care_code_link.admin_order_field = 'user__user_code'

    def get_birth_day(self, obj):
        return obj.user.birth_day.strftime(DEFAULT_DATE_FORMAT)

    get_birth_day.short_description = _('Ngày sinh')
    get_birth_day.admin_order_field = 'user__birth_day'

    def get_phone(self, obj):
        return obj.user.phone

    get_phone.short_description = _('Số điện thoại')
    get_phone.admin_order_field = 'user__phone'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = _('Email')
    get_email.admin_order_field = 'user__email'

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = _('username')
    get_username.admin_order_field = 'user__username'

    def get_address(self, obj):
        return obj.user.address

    get_address.short_description = _('address')
    get_address.admin_order_field = 'user__address'

    def get_date_joined(self, obj):
        return date_format(obj.user.date_joined, DEFAULT_DATE_FORMAT)

    get_date_joined.short_description = _('Ngày tham gia')
    get_date_joined.admin_order_field = 'user__date_joined'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return StudentCare.objects.filter(user__centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = self.list_filter
        if request.user.is_superuser:
            filters = ("user__centre",)
        return filters

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # context['adminform'].form.fields['user'].choices = CHOICE_EMPTY
        # choices = AuthUser.objects.filter(groups_id=GROUP.STUDENT_CARE).values_list('id', 'username')
        # if choices.count() > 0:
        #     context['adminform'].form.fields['user'].choices = CHOICE_EMPTY + list(choices)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def has_add_permission(self, request):
        return False
    pass


@admin.register(BusinessEmployee)
class BusinessEmployeeAdmin(BaseModelAdmin):
    list_display = ("id", "business_emp_code_link", "centre",
                    "get_username", "get_email", "get_birth_day",
                    "get_phone", "get_date_joined", "get_address")
    search_fields = ['user__username', 'user__full_name',
                     'user__user_code', 'user__email', "user__phone"]
    readonly_fields = ['user', 'get_username', 'get_email', 'created_user', 'updated_user']

    def business_emp_code_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.user.user_code)

    business_emp_code_link.short_description = "Mã nhân viên"
    business_emp_code_link.admin_order_field = 'user__user_code'

    def get_birth_day(self, obj):
        return obj.user.birth_day.strftime(DEFAULT_DATE_FORMAT)

    get_birth_day.short_description = _('Ngày sinh')
    get_birth_day.admin_order_field = 'user__birth_day'

    def get_phone(self, obj):
        return obj.user.phone

    get_phone.short_description = _('Số điện thoại')
    get_phone.admin_order_field = 'user__phone'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = _('Email')
    get_email.admin_order_field = 'user__email'

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = _('username')
    get_username.admin_order_field = 'user__username'

    def get_address(self, obj):
        return obj.user.address

    get_address.short_description = _('address')
    get_address.admin_order_field = 'user__address'

    def get_date_joined(self, obj):
        return date_format(obj.user.date_joined, DEFAULT_DATE_FORMAT)

    get_date_joined.short_description = _('Ngày tham gia')
    get_date_joined.admin_order_field = 'user__date_joined'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return StudentCare.objects.filter(user__centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = self.list_filter
        if request.user.is_superuser:
            filters = ("user__centre",)
        return filters

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # context['adminform'].form.fields['user'].choices = CHOICE_EMPTY
        # choices = AuthUser.objects.filter(groups_id=GROUP.STUDENT_CARE).values_list('id', 'username')
        # if choices.count() > 0:
        #     context['adminform'].form.fields['user'].choices = CHOICE_EMPTY + list(choices)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def has_add_permission(self, request):
        return False

    pass


@admin.register(Tests)
class TestsAdmin(BaseModelAdmin):
    inlines = [
        TestResultInline
    ]

    list_display = ("id", "title_link", "get_centre", "classes", "level", "content", "get_test_date")
    list_filter = ("classes__name", "level")
    search_fields = ['title', 'classes__centre__name', "classes__name", "content"]
    readonly_fields = ['created_user', 'updated_user']

    def get_centre(self, obj):
        return obj.classes.centre.name

    get_centre.short_description = _('Trung tâm')
    get_centre.admin_order_field = 'classes__centre__name'

    def title_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>", url=str(obj.id) + '/change', url_display=obj.title)

    title_link.short_description = _('Tiêu đề')
    title_link.admin_order_field = 'title'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        if request.user.groups.id == GROUP.STUDENT:
            # Truong hop la sinh vien
            return Tests.objects.filter(
                classes_id__in=ClassesStudents.objects.filter(
                    student__user=request.user).values_list("classes_id", flat=True))
        if request.user.groups.id == GROUP.TEACHER:
            # Truong hop la giao vien
            return Tests.objects.filter(
                classes_id__in=ClassesTeachers.objects.filter(
                    teacher__user=request.user).values_list("classes_id", flat=True))
        return Tests.objects.filter(classes__centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = self.list_filter
        if request.user.is_superuser:
            filters = ("classes__centre",) + filters

        return filters

    def get_test_date(self, obj):
        return obj.test_date.strftime(DEFAULT_DATE_FORMAT)

    get_test_date.short_description = _('Ngày diễn ra')
    get_test_date.admin_order_field = 'test_date'

    pass


@admin.register(Commendation)
class CommendationAdmin(BaseModelAdmin):
    list_display = ('code', 'title', 'centre')
    list_filter = (("students__user", custom_titled_filter('Học viên')),)
    search_fields = ['code', 'title', 'centre__name']
    readonly_fields = ['created_user', 'updated_user']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return Commendation.objects.filter(centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = self.list_filter
        if request.user.is_superuser:
            filters = ("centre",)
        return filters

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        choices = Student.objects.all().values_list('id', 'user__user_code')
        if choices.count() > 0:
            context['adminform'].form.fields['students'].choices = list(choices)
        return super().render_change_form(request, context, add, change, form_url, obj)

    pass
