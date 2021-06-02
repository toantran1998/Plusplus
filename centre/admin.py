from datetime import datetime, date, timedelta

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count, Case, When, IntegerField, F
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.utils.html import format_html
from django.utils.translation import gettext as _

from app_config.settings import DEFAULT_DATE_FORMAT
from centre.forms import ClassesForm
from centre.models import ClassRoom, Centre, StudyShift, StudyShiftTeacher, StudyShiftStudent, Course, Classes, \
    ClassesStudents, ClassesTeachers, Tasks, Issues, StudyShiftSchedule
from manager.admin import BaseModelAdmin, BaseTabularInline
from manager.constant import GROUP, CHOICE_EMPTY
from manager.utils import date_format, get_parent_object_from_request, currency
from message.views import send_inform_join_classes_to_teacher
from user.models import AuthUser, Student


class StudyShiftInline(BaseTabularInline):
    model = StudyShift
    fields = ('order_no', 'class_room', 'session_date', 'from_time', 'to_time')


@admin.register(Centre)
class CentreAdmin(BaseModelAdmin):
    icon_name = "home"
    list_display = (
        "id", "name_link", "count_receptionist", "count_student_care", "count_students", "count_teachers"
        , "count_class_room", "address")
    search_fields = ['name', 'address']
    readonly_fields = ['created_user', 'updated_user']

    def name_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>", url=str(obj.id) + '/change', url_display=obj.name)

    name_link.short_description = _('name')
    name_link.admin_order_field = 'name'

    def count_receptionist(self, obj):
        count_emps = AuthUser.objects.filter(
            Q(centre_id=obj.id), Q(groups_id=GROUP.RECEPTIONIST)).count()
        if count_emps > 0:
            return format_html(
                "<a href='/admin/user/receptionist/"
                "?centre__id__exact={centre_id}'>{url_display}</a>",
                centre_id=obj.id, group_id=str(GROUP.RECEPTIONIST), url_display=count_emps)
        return count_emps

    count_receptionist.short_description = _('Lễ tân')
    count_receptionist.admin_order_field = 'count_receptionist'

    def count_student_care(self, obj):
        count_emps = AuthUser.objects.filter(
            Q(centre_id=obj.id), Q(groups_id=GROUP.STUDENT_CARE)).count()
        if count_emps > 0:
            return format_html(
                "<a href='/admin/user/studentcare/"
                "?centre__id__exact={centre_id}'>{url_display}</a>",
                centre_id=obj.id, group_id=str(GROUP.STUDENT_CARE), url_display=count_emps)
        return count_emps

    count_student_care.short_description = _('Chăm sóc học viên')
    count_student_care.admin_order_field = 'count_student_care'

    def count_students(self, obj):
        count_emps = AuthUser.objects.filter(
            Q(centre_id=obj.id), Q(groups_id=GROUP.STUDENT)).count()

        if count_emps > 0:
            return format_html(
                "<a href='/admin/user/student/"
                "?centre__id__exact={centre_id}'>{url_display}</a>",
                centre_id=obj.id, url_display=count_emps)
        return count_emps

    count_students.short_description = _('Học viên')
    count_students.admin_order_field = 'count_students'

    def count_teachers(self, obj):
        count_emps = AuthUser.objects.filter(
            Q(centre_id=obj.id), Q(groups_id=GROUP.TEACHER)).count()

        if count_emps > 0:
            return format_html(
                "<a href='/admin/user/teacher/"
                "?centre__id__exact={centre_id}'>{url_display}</a>",
                centre_id=obj.id, url_display=count_emps)
        return count_emps

    count_teachers.short_description = _('giáo viên')
    count_teachers.admin_order_field = 'count_teachers'

    def count_class_room(self, obj):
        count_classes = ClassRoom.objects.filter(centre_id=obj.id).count()
        if count_classes > 0:
            return format_html(
                "<a href='/admin/centre/classroom/"
                "?centre__id__exact={centre_id}'>{url_display}</a>",
                centre_id=obj.id, url_display=count_classes)
        return count_classes

    count_class_room.short_description = _('Số phòng')
    count_class_room.admin_order_field = 'count_class_room'

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        if request.user.groups.id == GROUP.STUDENT:
            # Truong hop la sinh vien
            return Centre.objects.filter(
                id__in=ClassesStudents.objects.filter(
                    student__user=request.user).values_list("classes__centre__id", flat=True))
        if request.user.groups.id == GROUP.TEACHER:
            # Truong hop la giao vien
            return Centre.objects.filter(
                id__in=ClassesTeachers.objects.filter(
                    teacher__user=request.user).values_list("classes__centre__id", flat=True))
        return Centre.objects.filter(id=request.user.centre.id)

    pass


@admin.register(Tasks)
class TasksAdmin(BaseModelAdmin):
    change_list_template = "admin/tasks.html"

    def get_queryset(self, request):
        return Student.objects.none()
    
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StudyShiftSchedule)
class StudyShiftScheduleAdmin(BaseModelAdmin):
    change_list_template = "admin/study_shift_calendar.html"

    def get_queryset(self, request):
        return StudyShift.objects.none()

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ClassRoom)
class ClassRoomAdmin(BaseModelAdmin):
    list_display = ("id", "get_class_room_code", "name", "address", "size", "centre")
    list_filter = ("centre",)
    search_fields = ['name', 'address', 'centre__name']
    inlines = [StudyShiftInline]
    readonly_fields = ['created_user', 'updated_user']

    def get_class_room_code(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.class_room_code)

    get_class_room_code.short_description = "Mã phòng học"
    get_class_room_code.admin_order_field = "class_room_code"

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        return ClassRoom.objects.filter(centre__id=request.user.centre.id)

    pass


class StudyShiftStudentInline(BaseTabularInline):
    extra = 0
    model = StudyShiftStudent
    fields = ('student', 'attendance', 'leave_request', 'assessment', 'home_work', 'note')

    def get_queryset(self, request):
        # Chỉ hiện thị sinh viên còn trong lớp học của buổi học này
        study_shift = get_parent_object_from_request(self, request)
        student_ids = ClassesStudents.objects.filter(classes=study_shift.classes).values_list("student__id", flat=True)
        return StudyShiftStudent.objects.filter(student__id__in=student_ids)


class StudyShiftTeacherInline(BaseTabularInline):
    extra = 0
    model = StudyShiftTeacher
    fields = ('teacher', 'assessment_category', 'assessment', 'explain')

    def get_queryset(self, request):
        # Chỉ hiện thị giáo viên còn trong lớp học của buổi học này
        study_shift = get_parent_object_from_request(self, request)
        teachers_ids = ClassesTeachers.objects.filter(classes=study_shift.classes).values_list("teacher__id", flat=True)
        return StudyShiftTeacher.objects.filter(teacher__id__in=teachers_ids)


class CustomDateFieldListFilter(admin.SimpleListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.links = []
        session_date_list = list(
            StudyShift.objects.order_by('session_date').values_list('session_date', flat=True).distinct())
        for session_date in session_date_list:
            next_date = session_date + timedelta(days=1)
            self.links.insert(
                0, (session_date.strftime(DEFAULT_DATE_FORMAT),
                    {'session_date': str(session_date)}))

    def queryset(self, request, queryset):
        return queryset.filter(session_date=self.value())


class SessionDateListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Ngày diễn ra')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'date'

    def get_default_session_date(self, request):
        user = request.user

        if user.is_superuser or user.groups.id != GROUP.STUDENT_CARE:
            default_date = datetime.today()
        else:
            default_date = datetime.today() - timedelta(days=1)
        return default_date

    def __init__(self, request, params, model, model_admin):
        if 'date' not in request.GET and 'q' not in request.GET:
            default_date = self.get_default_session_date(request)
            if not request.GET._mutable:
                request.GET._mutable = True
            request.GET['date'] = default_date
        super().__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        session_date_list = list(
            StudyShift.objects.order_by('session_date').values_list('session_date', flat=True).distinct())
        choices = []
        for session_date in session_date_list:
            choices.insert(0, (str(session_date), session_date.strftime(DEFAULT_DATE_FORMAT)))

        default_date = self.get_default_session_date(request)
        choices.insert(0, (default_date.strftime("%Y-%m-%d"), default_date.strftime(DEFAULT_DATE_FORMAT)))
        return choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(session_date=self.value())

        # Truong hop chon tat ca date.
        if 'q' in request.GET:
            return queryset
        # Truong hop khoi tao man hinh.
        default_date = self.get_default_session_date(request)
        return queryset.filter(session_date=default_date)


@admin.register(StudyShift)
class StudyShiftAdmin(BaseModelAdmin):
    inlines = [StudyShiftTeacherInline, StudyShiftStudentInline]
    list_display = ("id", "order_no_link", "get_classes",
                    "get_classes_room", "get_session_date", "study_shift_select",
                    "from_time", "to_time", "get_attendance_info", "get_state")
    fields = ("order_no", "classes", "class_room", "session_date", "study_shift_select",
              "from_time", "to_time", 'created_user', 'updated_user')
    readonly_fields = ['created_user', 'updated_user']
    finished_readonly_fields = ['order_no', 'classes', 'class_room', 'session_date', 'study_shift_select',
                                'from_time', 'to_time', 'created_user', 'updated_user']
    list_filter = ("classes__day_in_week", "study_shift_select", SessionDateListFilter)
    search_fields = ['order_no', 'classes__centre__name', "classes__name", "class_room__name"]
    # date_hierarchy = 'session_date'

    def get_attendance_info(self, obj):
        sys_date_time = datetime.today()
        from_date_time = datetime.combine(obj.session_date, obj.from_time)
        # Nếu buổi học chưa diễn ra
        if sys_date_time < from_date_time:
            return '-'

        attendance_info = StudyShiftStudent.objects.filter(study_shift=obj) \
            .values('student_id', 'attendance').annotate(
            count_absent=Count(Case(
                When(attendance=False, then=1),
                output_field=IntegerField(),
            ))).annotate(
            count_attendance=Count(Case(
                When(attendance=True, then=1),
                output_field=IntegerField(),
            ))).annotate(count_total=Count('student_id')).values('count_absent', 'count_attendance', 'count_total')

        # Trường hợp buổi học chưa có sv nào
        if not attendance_info:
            return "-"
        return "%s/%s/%s" %(str(attendance_info[0]['count_absent']),
                            str(attendance_info[0]['count_attendance']),
                            str(attendance_info[0]['count_total']))
    get_attendance_info.short_description = "Vắng mặt/Có mặt/Tổng SV"

    def order_no_link(self, obj):
        return obj.order_no

    order_no_link.short_description = _('STT buổi')
    order_no_link.admin_order_field = 'order_no'

    def get_centre(self, obj):
        return obj.classes.centre.name

    get_centre.short_description = _('Trung tâm')
    get_centre.admin_order_field = 'classes__centre__name'

    def get_classes(self, obj):
        return obj.classes.name

    get_classes.short_description = _('Lớp học')
    get_classes.admin_order_field = 'classes__name'

    def get_classes_room(self, obj):
        return obj.class_room.name

    get_classes_room.short_description = _('Phòng học')
    get_classes_room.admin_order_field = 'class_room__name'

    def get_inlines(self, request, obj):
        if obj and obj.pk:
            return self.inlines
        return []

    # def get_urls(self):
    #     urls = super(StudyShiftAdmin, self).get_urls()
    #     urls[0].default_args['date'] = "2021-01-01"
    #     return urls

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)
        if request.user.groups.id == GROUP.STUDENT:
            # Truong hop la sinh vien
            return StudyShift.objects.filter(
                classes_id__in=ClassesStudents.objects.filter(
                    student__user=request.user).values_list("classes_id", flat=True))
        if request.user.groups.id == GROUP.TEACHER:
            # Truong hop la giao vien
            return StudyShift.objects.filter(
                classes_id__in=ClassesTeachers.objects.filter(
                    teacher__user=request.user).values_list("classes_id", flat=True))

        return StudyShift.objects.filter(classes__centre__id=request.user.centre.id)

    def get_readonly_fields(self, request, obj=None):
        if obj and datetime.today() >= datetime.combine(obj.session_date, obj.from_time):
            return self.finished_readonly_fields
        return self.readonly_fields

    def get_list_filter(self, request):
        # filters = (('session_date', DateRangeFilter), )
        filters = self.list_filter
        if request.user.is_superuser:
            filters = ("classes__centre",) + filters

        return filters

    def get_session_date(self, obj):
        return date_format(obj.session_date, DEFAULT_DATE_FORMAT)

    get_session_date.short_description = _('Ngày diễn ra')
    get_session_date.admin_order_field = 'session_date'

    def get_state(self, obj):
        sys_date_time = datetime.today()
        from_date_time = datetime.combine(obj.session_date, obj.from_time)
        to_date_time = datetime.combine(obj.session_date, obj.to_time)
        if sys_date_time < from_date_time:
            return 'Chưa bắt đầu'
        elif sys_date_time > to_date_time:
            return 'Đã kết thúc'
        else:
            return 'Đang diễn ra'

    get_state.short_description = "Trạng thái"
    get_state.admin_order_field = "session_date"

    def has_delete_permission(self, request, obj=None):
        return obj and datetime.today() < datetime.combine(obj.session_date, obj.from_time)

    # def has_change_permission(self, request, obj=None):
    #     return obj and datetime.today() < datetime.combine(obj.session_date, obj.from_time)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        fields = context['adminform'].form.fields
        if 'classes' in fields:
            context['adminform'].form.fields['classes'].choices = CHOICE_EMPTY
            choices = Classes.objects.filter(waiting_flag=False).values_list('id', 'name')
            if choices.count() > 0:
                context['adminform'].form.fields['classes'].choices = CHOICE_EMPTY + list(choices)
        if 'class_room' in fields and not request.user.is_superuser:
            context['adminform'].form.fields['class_room'].choices = CHOICE_EMPTY
            choices = ClassRoom.objects.filter(centre=request.user.centre).values_list('id', 'name')
            if choices.count() > 0:
                context['adminform'].form.fields['class_room'].choices = CHOICE_EMPTY + list(choices)

        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        super(StudyShiftAdmin, self).save_model(request, obj, form, change)

        # Trường hợp tạo mới => add các sinh viên vs giáo viên thuộc lớp học vào buổi học.
        if not change:
            # Add giáo viên vào buổi học
            classes_teachers = ClassesTeachers.objects.filter(classes=obj.classes)
            if classes_teachers.count() > 0:
                for classes_teacher in classes_teachers:
                    study_shift_teacher = StudyShiftTeacher(study_shift_id=obj.id,
                                                            teacher_id=classes_teacher.teacher.id)
                    study_shift_teacher.save()

            # Add sinh viên có trạng thái chưa hoàn thành vào buổi học
            classes_students = ClassesStudents.objects.filter(classes=obj.classes, state=0)
            if classes_students.count() > 0:
                for classes_student in classes_students:
                    study_shift_student = StudyShiftStudent(study_shift_id=obj.id,
                                                            student_id=classes_student.student.id)
                    study_shift_student.save()

    def delete_model(self, request, obj):
        super(StudyShiftAdmin, self).delete_model(request, obj)
        # update ds study shift
        update_study_shifts(obj.classes, request.user)
    pass


class IssuesStudentFilter(SimpleListFilter):
    title = 'Học viên'
    parameter_name = 'student_id'

    def lookups(self, request, model_admin):
        students = list(Issues.objects.annotate(
            student_code=F('student__user__user_code'),
            student_name=F("student__user__full_name")).values(
            "student_id", "student_code", "student_name").distinct())
        choices = []
        for s in students:
            choices.insert(0, (str(s['student_id']), s['student_name'] + ' (' + s['student_code'] + ')'))

        return choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(student_id=self.value())
        else:
            return queryset


class IssuesClassesFilter(SimpleListFilter):
    title = 'Lớp học'
    parameter_name = 'classes_id'

    def lookups(self, request, model_admin):
        classes = list(Issues.objects.annotate(
            classes_code=F('classes__code'),
            classes_name=F("classes__name")).values(
            "classes_id", "classes_code", "classes_name").distinct())
        choices = []
        for c in classes:
            choices.insert(0, (str(c['classes_id']), c['classes_name']))

        return choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(classes_id=self.value())
        else:
            return queryset


@admin.register(Issues)
class IssuesAdmin(BaseModelAdmin):
    list_display = ("id", "get_title_link", "centre", "get_course", "classes", "get_student_name", "get_student_code", "get_student_email"
                    , "get_student_phone", "content", "category", "state")
    search_fields = ['title', 'student__user__full_name', "student__user__phone", "student__user__user_code",
                     "student__user__email", 'centre__name', 'classes__course__name']
    readonly_fields = ['created_user', 'updated_user']
    # all_readonly_fields = ['centre', 'course', 'name', 'day_in_week', 'start_date', 'study_shift_select',
    #                        'end_date', 'code', 'created_user', 'updated_user', 'end_date']
    list_filter = (IssuesClassesFilter,
                   IssuesStudentFilter,
                   "category", "state")

    def get_title_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.title)
    get_title_link.short_description = "Tiêu đề"
    get_title_link.admin_order_field = 'title'

    def get_student_name(self, obj):
        return obj.student.user.full_name

    get_student_name.short_description = 'Họ và tên'
    get_student_name.admin_order_field = 'student__user__full_name'

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

    def get_course(self, obj):
        return obj.classes.course

    get_course.short_description = 'Khóa học'
    get_course.admin_order_field = 'classes_course__name'

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.id == GROUP.STUDENT\
               or request.user.groups.id == GROUP.STUDENT_CARE

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.id == GROUP.STUDENT \
               or request.user.groups.id == GROUP.STUDENT_CARE
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.id == GROUP.STUDENT_CARE
    def has_delete_permission(self, request, obj=None):
        if obj and obj.created_user:
            return request.user.id == obj.created_user.id
        return False

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)

        if request.user.groups.id == GROUP.STUDENT:
            # Truong hop la sinh vien
            return super(BaseModelAdmin, self).get_queryset(request).filter(
                    student__user=request.user)
        return super(BaseModelAdmin, self).get_queryset(request).filter(centre__id=request.user.centre.id)

    # def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
    #     fields = context['adminform'].form.fields
    #     if 'student' in fields:
    #         context['adminform'].form.fields['student'].choices = CHOICE_EMPTY
    #         choices = Classes.objects.filter(waiting_flag=False).values_list('id', 'name')
    #         if choices.count() > 0:
    #             context['adminform'].form.fields['student'].choices = CHOICE_EMPTY + list(choices)
    #
    #     return super().render_change_form(request, context, add, change, form_url, obj)

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ("centre",) + self.list_filter
        if request.user.groups.id == GROUP.STUDENT:
            return []
        return self.list_filter

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        fields = context['adminform'].form.fields
        if not obj:
            if 'student' in fields:
                if not request.user.is_superuser:
                    if request.user.groups.id == GROUP.STUDENT:
                        context['adminform'].form.fields['student'].choices =\
                            [(Student.objects.get(user=request.user).id, (request.user.full_name + " (" + request.user.user_code + ")"))]
                    else:
                        context['adminform'].form.fields['student'].choices = CHOICE_EMPTY
                        choices = Student.objects.filter(user__centre=request.user.centre) \
                            .annotate(user_label=Concat('user__full_name', V(' ('), 'user__user_code', V(')'))) \
                            .values_list('id', 'user_label')
                        if choices.count() > 0:
                            context['adminform'].form.fields['student'].choices = CHOICE_EMPTY + list(choices)

        return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(Course)
class CourseAdmin(BaseModelAdmin):
    list_display = ("id", "get_name_link", "get_cost", "get_day_cost", "get_night_cost", "description", "count_classes"
                    , "study_shift_count")
    readonly_fields = ['created_user', 'updated_user']
    search_fields = ['name', 'centre__name']

    def get_name_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.name)

    get_name_link.short_description = "Tiêu đề"
    get_name_link.admin_order_field = 'name'

    def get_cost(self, obj):
        return currency(obj.cost)

    get_cost.short_description = "Giá gốc"
    get_cost.admin_order_field = 'cost'

    def get_day_cost(self, obj):
        return currency(obj.daytime_cost)

    get_day_cost.short_description = "Giá ca ngày"
    get_day_cost.admin_order_field = 'daytime_cost'

    def get_night_cost(self, obj):
        return currency(obj.night_cost)

    get_night_cost.short_description = "Giá ca tối"
    get_night_cost.admin_order_field = 'night_cost'

    # def get_queryset(self, request):
    #     if request.user.is_superuser:
    #         return super(BaseModelAdmin, self).get_queryset(request).annotate(models.Count('classes'))
    #     return Course.objects.filter(centre__id=request.user.centre.id).annotate(models.Count('classes'))

    # def get_list_filter(self, request):
    #     filters = self.list_filter
    #     if request.user.is_superuser:
    #         filters = ("centre",) + filters
    #
    #     return filters

    def count_classes(self, obj):
        return Classes.objects.filter(course__id=obj.id).count()

    count_classes.short_description = _('Số lớp học')
    count_classes.admin_order_field = 'classes__count'

    pass


# Tab inline For parent is classes
class ClassesStudentInline(BaseTabularInline):
    extra = 0
    model = ClassesStudents
    fields = ("student", "get_student_name", "get_student_code", "get_student_email",
              "get_student_phone",
              "get_rest_amount",
              "get_attendance", "get_team", 'state')
    waiting_cls_fields = ("get_student_name", "get_student_code", "get_student_email",
                          "get_student_phone",
                          "get_rest_amount",
                          "get_study_shift_select", "get_team", 'state')
    readonly_fields = ('get_student_name', 'get_student_code',
                       "get_student_email",
                       "get_study_shift_select",
                       "get_student_phone", "get_rest_amount",
                       "get_attendance", "get_team")
    waiting_readonly_fields = readonly_fields + ("state",)
    verbose_name = "Sinh viên"
    verbose_name_plural = "Sinh viên"

    def get_fields(self, request, obj=None):
        if obj and obj.waiting_flag:
            return self.waiting_cls_fields
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.waiting_flag:
            return self.waiting_readonly_fields
        return self.readonly_fields

    def get_attendance(self, obj):
        return StudyShiftStudent.objects.filter(
            study_shift__classes=obj.classes, student=obj.student, attendance=True).count()
    get_attendance.short_description = 'Chuyên cần'

    def get_study_shift_select(self, obj):
        return obj.student_debt.get_study_schedule_select_display()
    get_study_shift_select.short_description = 'Ca học'

    def get_team(self, obj):
        return obj.student_debt.counselor
    get_team.short_description = 'Đội'

    def get_student_name(self, obj):
        return obj.student.user.full_name
    get_student_name.short_description = 'Họ và tên'

    def get_student_code(self, obj):
        return obj.student.user.user_code
    get_student_code.short_description = 'Mã HV'

    def get_student_email(self, obj):
        return obj.student.user.email
    get_student_email.short_description = 'Email'

    def get_student_phone(self, obj):
        return obj.student.user.phone
    get_student_phone.short_description = 'Số ĐT'

    def get_action_list(self, obj):
        return format_html('<a href="#">Delete</a>')
    get_action_list.short_description = 'Action'

    def get_rest_amount(self, obj):
        rest_amount = obj.student_debt.rest_amount
        if rest_amount == 0:
            return 'Đã hoàn thành'
        return currency(rest_amount)
    get_rest_amount.short_description = 'Học phí còn lại'

    def get_queryset(self, request):
        query = super(ClassesStudentInline, self).get_queryset(request)
        # ẩn những sv trong lớp ở trạng thái hủy
        query = query.filter(~Q(state=7))
        return query

    def get_field_queryset(self, db, db_field, request):
        if db_field.column == 'student_id':
            # Loc ra nhung sinh vien da dc add vao khoa hoc va dang o lop chờ.
            parent_class = get_parent_object_from_request(self, request)
            if parent_class:
                # Nếu có lớp chờ của khoá tương ứng => chọn ra những sv thuộc lớp chờ để làm dữ liệu input.
                #toan sửa
                wait_classes_list = Classes.objects.filter(
                                                       centre=parent_class.centre, waiting_flag=True)

                print(wait_classes_list)
                if wait_classes_list.count() > 0:
                    waiting_classes_list = []
                    for waiting_classes in wait_classes_list:
                        waiting_classes_list.append(waiting_classes.id)
                    # qs = super(ClassesStudents, self).get_queryset(request)
                    # return qs.filter(classes_id=waiting_classes.id)
                    return Student.objects.filter(
                        id__in=ClassesStudents.objects.filter(
                            Q(classes_id=parent_class.id) | Q(classes_id__in=waiting_classes_list)
                        ).values_list('student_id'))
                # end

    def has_add_permission(self, request, obj):
        return obj and obj.pk and not obj.waiting_flag

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.id == GROUP.STUDENT_CARE


class ClassesTeachersInline(BaseTabularInline):
    extra = 1
    model = ClassesTeachers
    fields = ('teacher', 'get_name', 'get_code', 'get_email', 'get_phone', 'assessment', 'note')
    readonly_fields = ('get_name', 'get_code', 'get_email', 'get_phone')
    verbose_name = "Giáo viên"
    verbose_name_plural = "Giáo viên"

    def get_name(self, obj):
        return obj.teacher.user.full_name
    get_name.short_description = 'Họ và tên'

    def get_code(self, obj):
        return obj.teacher.user.user_code
    get_code.short_description = 'Mã GV'

    def get_email(self, obj):
        return obj.teacher.user.email
    get_email.short_description = 'Email'

    def get_phone(self, obj):
        return obj.teacher.user.phone
    get_phone.short_description = 'Số ĐT'

    # def get_fields(self, request, obj=None):
    #     if not obj:
    #         return self.fields
    #     return self.exists_fields
    #
    # def get_readonly_fields(self, request, obj=None):
    #     if not obj:
    #         return self.readonly_fields
    #     return self.exists_readonly_fields

    def has_add_permission(self, request, obj):
        return obj and obj.pk

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.id == GROUP.STUDENT_CARE


class ClassesStartDateListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Ngày khai giảng')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'start_date'

    def lookups(self, request, model_admin):
        start_date_list = list(
            Classes.objects.order_by('start_date').values_list('start_date', flat=True).distinct())
        choices = []
        for start_date in start_date_list:
            choices.insert(0, (str(start_date), start_date.strftime(DEFAULT_DATE_FORMAT)))

        return choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(start_date=self.value())

        # Truong hop ko chọn date.
        return queryset


@admin.register(Classes)
class ClassesAdmin(BaseModelAdmin):
    list_display = ("id", "get_name_link", "code", "centre", "course", "get_day_in_week", "get_start_date", "get_end_date"
                    , "show_students_count", "show_teachers_count"
                    , "get_state", "get_created_date_time")
    search_fields = ['code', 'name', 'centre__name', 'course__name']
    readonly_fields = ['code', 'created_user', 'updated_user', 'end_date']
    all_readonly_fields = ['centre', 'course', 'name', 'day_in_week', 'start_date', 'study_shift_select',
                           'end_date', 'code', 'created_user', 'updated_user', 'end_date', 'waiting_flag']
    list_filter = (ClassesStartDateListFilter, "day_in_week", "created_date_time",)
    waiting_class_inlines = [ClassesStudentInline]
    normal_class_inlines = [StudyShiftInline, ClassesTeachersInline, ClassesStudentInline]
    inlines = [ClassesTeachersInline, ClassesStudentInline]
    form = ClassesForm

    def get_day_in_week(self, obj):
        return obj.get_day_in_week_display()
    get_day_in_week.short_description = "Lịch học"
    get_day_in_week.admin_order_field = "day_in_week"

    def get_created_date_time(self, obj):
        return obj.created_date_time.strftime(DEFAULT_DATE_FORMAT)
    get_created_date_time.short_description = "Ngày tạo"
    get_created_date_time.admin_order_field = "created_date_time"

    def get_start_date(self, obj):
        if obj.waiting_flag:
            return None
        return obj.start_date.strftime(DEFAULT_DATE_FORMAT)
    get_start_date.short_description = "Ngày khai giảng"
    get_start_date.admin_order_field = "start_date"

    def get_end_date(self, obj):
        if obj.waiting_flag:
            return None
        return obj.end_date.strftime(DEFAULT_DATE_FORMAT)
    get_end_date.short_description = "Ngày kết thúc"
    get_end_date.admin_order_field = "end_date"

    # def has_delete_permission(self, request, obj=None):
    #     return True

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(BaseModelAdmin, self).get_queryset(request)

        if request.user.groups.id == GROUP.STUDENT:
            # Truong hop la sinh vien
            return Classes.objects.filter(
                id__in=ClassesStudents.objects.filter(
                    student__user=request.user).values_list("classes_id", flat=True))
        if request.user.groups.id == GROUP.TEACHER:
            # Truong hop la giao vien
            return Classes.objects.filter(
                id__in=ClassesTeachers.objects.filter(
                    teacher__user=request.user).values_list("classes_id", flat=True))
        return Classes.objects.filter(centre__id=request.user.centre.id)

    def get_list_filter(self, request):
        filters = self.list_filter
        if request.user.is_superuser:
            filters = ("centre",) + filters

        return filters

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk:
            return self.all_readonly_fields
        return self.readonly_fields

    def get_state(self, obj):
        if obj.waiting_flag:
            return "-"
        sys_date = date.today()
        if sys_date < obj.start_date:
            return 'Chưa bắt đầu'
        elif obj.start_date <= sys_date <= obj.end_date:
            return 'Đang diễn ra'
        else:
            return 'Đã kết thúc'

    get_state.short_description = "Trạng thái"
    # get_state.admin_order_field = "start_date"

    def get_name_link(self, obj):
        return format_html("<a href='{url}'>{url_display}</a>",
                           url=str(obj.id) + '/change', url_display=obj.name)

    def show_students_count(self, obj):
        return ClassesStudents.objects.filter(Q(classes_id=obj.id), ~Q(state=7)).count()

    def show_teachers_count(self, obj):
        return ClassesTeachers.objects.filter(classes_id=obj.id).count()

    get_name_link.short_description = "Tên lớp học"
    get_name_link.admin_order_field = 'name'
    show_students_count.short_description = "Số sinh viên"
    # show_students_count.admin_order_field = 'student_count'
    show_teachers_count.short_description = "Số giáo viên"
    # show_teachers_count.admin_order_field = 'teacher_count'

    def get_inlines(self, request, obj):
        if obj and obj.pk:
            if obj.waiting_flag:
                return self.waiting_class_inlines
            return self.normal_class_inlines
        return self.inlines

    def save_model(self, request, obj, form, change):
        super(ClassesAdmin, self).save_model(request, obj, form, change)

        if not change:
            # Sinh tu dong ma lop hoc
            obj.code = obj.course.code + '_' + datetime.now().strftime("%y%m") + '_' + str(obj.id).zfill(3)
            obj.save()

            # Tu dong tao ra danh sach buoi hoc dua vao ngay bat dau va so buoi hoc
            if not obj.waiting_flag:
                study_shift_count = obj.course.study_shift_count
                next_start_date = obj.start_date
                create_study_shifts(obj, study_shift_count, next_start_date, 1, request.user)

        # classes_students = ClassesStudents.objects.filter(classes=obj.classes)
        # if classes_students.count() > 0:
        #     for classes_student in classes_students:
        #         study_shift_student = StudyShiftStudent(study_shift_id=obj.id, student_id=classes_student.student.id)
        #         study_shift_student.save()

    def save_related(self, request, form, formsets, change):
        # inform to teacher if add teacher to class
        add_teachers = []
        cls = form.instance
        for formset in formsets:
            if formset.prefix == 'classesteachers_set':
                cleaned_data = formset.cleaned_data
                for data in cleaned_data:
                    if 'teacher' in data:
                        teacher = data['teacher']
                        # Trường hợp add giáo viên
                        if ClassesTeachers.objects.filter(classes=cls, teacher=teacher).count() == 0:
                            add_teachers.append(teacher.user)

        super(ClassesAdmin, self).save_related(request, form, formsets, change)

        for user in add_teachers:
            send_inform_join_classes_to_teacher(user, cls)

        if not cls.waiting_flag:
            # Đối với sinh viên đã tham gia lớp và chưa hoàn thành => Cần add các sv đó vào các buổi học của lớp học
            # Get ds sinh viên được thêm vào lớp học này và ở trạng thái là chờ xếp lớp
            classes_students = ClassesStudents.objects.filter(classes_id=cls.id, state=1)

            # Get ds sv vẫn chưa được xóa khỏi lớp chờ của khóa học đó.
            waiting_classes_students = ClassesStudents.objects.filter(
                classes__course_id=cls.course.id, student_id__in=list(classes_students.values_list('student_id')),
                classes__waiting_flag=True, classes__centre=cls.centre)
            # Gắn student_debt và next_course_code của sv trong lớp học
            for wcs in waiting_classes_students:
                cls_stu = ClassesStudents.objects.get(student=wcs.student, classes=cls)
                cls_stu.student_debt = wcs.student_debt
                cls_stu.next_course_code = wcs.next_course_code
                cls_stu.save()

            # Xóa sv được thêm vào lớp học này ra khỏi lớp chờ của khóa học đó.
            waiting_classes_students.delete()

            # Add sinh viên vào các buổi học chưa bắt đầu của lớp này (Xu ly cho nhieu sinh vien).
            study_shifts = StudyShift.objects.filter(classes_id=cls.id)
            for class_student in classes_students:
                # add sv vào các buổi học, cập nhật trạng thái của sv là nhận lớp
                # Set trạng thái sv là nhận lớp
                class_student.state = 2
                add_student_to_study_shift(class_student, study_shifts)

            # Add giáo viên vào các buổi học chưa bắt đầu của lớp này.
            classes_teachers = ClassesTeachers.objects.filter(classes_id=cls.id)
            for class_teacher in classes_teachers:
                # Trường hợp giao viên chưa được thêm vào các buổi học.
                if not class_teacher.added_study_shift:
                    for study_shift in study_shifts:
                        sys_date_time = datetime.today()
                        from_date_time = datetime.combine(study_shift.session_date, study_shift.from_time)
                        # Nếu buổi học chưa diễn ra
                        if sys_date_time < from_date_time:
                            study_shift_teacher = StudyShiftTeacher(study_shift_id=study_shift.id,
                                                                    teacher_id=class_teacher.teacher.id)
                            study_shift_teacher.save()

                    # Cập nhật trạng thái là giáo viên đã được thêm vào các buổi học
                    class_teacher.added_study_shift = True
                    class_teacher.save()

            # Cap nhat ds buoi hoc
            update_study_shifts(cls, request.user)

            # Xử lý tốt nghiệp cho các sinh viên có đăng ký khóa commbo.
            # Tự động add sv vào lớp chờ của khóa tiếp theo.
            graduated_cls_students = ClassesStudents.objects.filter(classes_id=cls.id, state=3)
            for gcs in graduated_cls_students:
                student_debt = gcs.student_debt
                next_course_code = gcs.next_course_code
                # Trường hợp sv có mã khóa tiếp theo
                if next_course_code:
                    # Check xem sv đã được add vào lớp học của khóa đó chưa.
                    # Nếu chưa thì thực hiện add sv vào lớp chờ của khóa đó.
                    if ClassesStudents.objects.filter(student_debt=student_debt, classes__course__code=next_course_code).count() == 0:
                        # Get khóa tiếp theo nữa của sv từ mã khóa combo
                        combo_course_code_array = student_debt.course.code.split('_')
                        next_next_course_code = None
                        for i in range(len(combo_course_code_array)):
                            if combo_course_code_array[i] == next_course_code and i < len(combo_course_code_array) - 1:
                                next_next_course_code = combo_course_code_array[i + 1]
                        waiting_classes = Classes.objects.get(course__code=next_course_code,
                                                              day_in_week=gcs.classes.day_in_week, waiting_flag=True)
                        w_class_student = ClassesStudents(classes=waiting_classes, student=student_debt.student,
                                                          student_debt=student_debt, next_course_code=next_next_course_code,
                                                          updated_user=request.user, created_user=request.user)
                        # add student into waiting class of course
                        w_class_student.save()

            # Đối với những sv hủy(xóa) khỏi lớp
            cancel_cls_students = ClassesStudents.objects.filter(classes_id=cls.id, state=7)
            for ccs in cancel_cls_students:
                # Can xoa nhung buoi hoc chua dien ra cua sinh vien o lop nay
                ss_shifts = StudyShiftStudent.objects.filter(student=ccs.student, study_shift__classes=ccs.classes)
                for ss_student in ss_shifts:
                    sys_date_time = datetime.today()
                    from_date_time = datetime.combine(
                        ss_student.study_shift.session_date, ss_student.study_shift.from_time)
                    # Nếu buổi học chưa diễn ra
                    if sys_date_time < from_date_time:
                        ss_student.delete()

    pass


# Tạo danh sách buổi học còn thiếu của một lớp học và cập nhật lại thứ tự các buổi.
# Trường hợp lớp học chưa có buổi nào => tạo mới ds buổi học.
# Sau khi tạo ds buổi học thành công => cập nhật lại thời gian kết thúc của lớp học.
def update_study_shifts(cls, create_user):
    study_shifts = StudyShift.objects.filter(classes=cls)
    require_study_shift_count = cls.course.study_shift_count
    count = study_shifts.count()
    # Trường hợp lớp học chưa có buổi nào
    if count == 0:
        # Tu dong tao ra danh sach buoi hoc dua vao ngay bat dau va so buoi hoc
        study_shift_count = cls.course.study_shift_count
        create_study_shifts(cls, study_shift_count, cls.start_date, 1, create_user)

    # Trường hợp lớp học chưa đủ số lượng buổi theo yêu cầu
    elif count < require_study_shift_count:
        # Cập nhật lại order_no của các buổi học hiện tại
        for i in range(count):
            print('range count:i=' + str(i))
            study_shift = StudyShift.objects.get(id=study_shifts[i].id)
            study_shift.order_no = (i + 1)
            study_shift.save()
            # Cap nhat lai ngay khai giang lop hoc vi co the user xoa buoi dau tien cua lop.
            if i == 0:
                cls.start_date = study_shift.session_date

        # Tạo mới các buổi học còn thiếu
        # Số buổi cần tạo thêm
        must_add_count = require_study_shift_count - study_shifts.count()
        # Ngày diễn ra buổi học tiếp theo
        next_start_date = get_next_start_date(cls.end_date)
        create_study_shifts(cls, must_add_count, next_start_date, (count + 1), create_user)


# Get thời gian buổi học tiếp theo dựa trên thời gian của buổi hiện tại
def get_next_start_date(day_in_week, current_start_date):
    next_start_week_day = current_start_date.weekday()

    # chon lich hoc
    print(day_in_week)
    if day_in_week <= 3:
        if next_start_week_day <= 2:
            return current_start_date + timedelta(days=3)
        return current_start_date + timedelta(days=4)

    if day_in_week ==4:
        if next_start_week_day == 0:
            return current_start_date + timedelta(days=2)
        return current_start_date + timedelta(days=5)

    if day_in_week == 5:
        if next_start_week_day == 0:
            return current_start_date + timedelta(days=4)
        return current_start_date + timedelta(days=3)
    if day_in_week == 6:
        if next_start_week_day == 2:
            return current_start_date + timedelta(days=5)
        return current_start_date + timedelta(days=2)
    if day_in_week == 7:
        if next_start_week_day == 1:
            return current_start_date + timedelta(days=2)
        return current_start_date + timedelta(days=5)
    if day_in_week == 8:
        if next_start_week_day == 1:
            return current_start_date + timedelta(days=4)
        return current_start_date + timedelta(days=3)
    if day_in_week == 9:
        if next_start_week_day == 1:
            return current_start_date + timedelta(days=5)
        return current_start_date + timedelta(days=2)
    if day_in_week == 10:
        if next_start_week_day == 2:
            return current_start_date + timedelta(days=2)
        return current_start_date + timedelta(days=5)
    if day_in_week == 11:
        if next_start_week_day == 2:
            return current_start_date + timedelta(days=4)
        return current_start_date + timedelta(days=3)
    if day_in_week == 12:
        if next_start_week_day == 3:
            return current_start_date + timedelta(days=2)
        return current_start_date + timedelta(days=5)
    if day_in_week == 13:
        if next_start_week_day == 3:
            return current_start_date + timedelta(days=3)
        return current_start_date + timedelta(days=4)
    if day_in_week == 14:
        if next_start_week_day == 4:
            return current_start_date + timedelta(days=2)
        return current_start_date + timedelta(days=5)
    return current_start_date + timedelta(days=4)
    # Tinh toan ngay tiep theo
    # if next_start_week_day <= 2:
    #     return current_start_date + timedelta(days=3)
    # return current_start_date + timedelta(days=4)


# Tạo một số lượng buổi học
def create_study_shifts(cls, study_shift_count, next_start_date, next_start_order_no, create_user):
    from_time = None
    to_time = None
    # chon ca hoc
    if cls.study_shift_select == 1:
        from_time = datetime.strptime("19:00", "%H:%M")
        to_time = datetime.strptime("21:00", "%H:%M")
    elif cls.study_shift_select == 2:
        from_time = datetime.strptime("19:30", "%H:%M")
        to_time = datetime.strptime("21:30", "%H:%M")
    elif cls.study_shift_select == 3:
        from_time = datetime.strptime("18:00", "%H:%M")
        to_time = datetime.strptime("20:00", "%H:%M")
    elif cls.study_shift_select == 4:
        from_time = datetime.strptime("18:30", "%H:%M")
        to_time = datetime.strptime("20:30", "%H:%M")
    elif cls.study_shift_select == 5:
        from_time = datetime.strptime("21:00", "%H:%M")
        to_time = datetime.strptime("23:00", "%H:%M")
    elif cls.study_shift_select == 6:
        from_time = datetime.strptime("20:00", "%H:%M")
        to_time = datetime.strptime("22:00", "%H:%M")
    for i in range(study_shift_count):
        study_shift = StudyShift(classes=cls, class_room_id=1, order_no=(i + next_start_order_no),
                                 session_date=next_start_date, study_shift_select=cls.study_shift_select,
                                 from_time=from_time, to_time=to_time,
                                 created_user=create_user, updated_user=create_user)
        study_shift.save()

        # Cập nhật lại thời gian end_date của lớp học
        if i == study_shift_count - 1:
            cls.end_date = next_start_date

        next_start_date = get_next_start_date(cls.day_in_week, next_start_date)

    cls.save()


# Add sv vao cac buoi hoc chua dien ra
def add_student_to_study_shift(class_student, study_shifts=None):
    if not study_shifts:
        study_shifts = StudyShift.objects.filter(classes=class_student.classes)

    # Trường hợp sinh viên chưa được thêm vào các buổi học
    if not class_student.added_study_shift:
        for study_shift in study_shifts:
            sys_date_time = datetime.today()
            from_date_time = datetime.combine(study_shift.session_date, study_shift.from_time)
            # Nếu buổi học chưa diễn ra
            if sys_date_time < from_date_time:
                study_shift_student = StudyShiftStudent(study_shift_id=study_shift.id,
                                                        student_id=class_student.student.id)
                study_shift_student.save()

        # Cập nhật trạng thái là sinh viên đã được thêm vào các buổi học
        class_student.added_study_shift = True
        class_student.save()
