from datetime import date

from django.contrib.auth import password_validation
from django.contrib.auth.models import Group, AbstractUser, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from centre.models import Classes, Course, StudyShift
from manager.utils import create_user_label


class AuthUser(AbstractUser):
    full_name = models.CharField(_('Họ và tên'), max_length=150, default=None)
    first_name = models.CharField(editable=False, default=None, null=True, blank=True, max_length=150)
    last_name = models.CharField(editable=False, default=None, null=True, blank=True, max_length=150)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Yêu cầu bắt buộc nhập, chỉ cho phép nhập tối đa 150 ký tự tiếng Anh hoặc ký tự số'),
        validators=[RegexValidator(
            regex="^[a-zA-Z0-9]*$",
            message=_('Enter a valid username.'),
        )],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    user_code = models.CharField(_('Mã người dùng'), max_length=10, unique=True, default=None, null=True, editable=False,
                                 help_text=_('Yêu cầu bắt buộc nhập,'
                                             ' chỉ cho phép nhập tối đa 10 ký tự tiếng Anh hoặc ký tự số'), )

    email = models.EmailField(_('Email'), unique=True)
    phone = models.CharField(_('Phone'), max_length=11, default=None, validators=[RegexValidator(
        regex="^\+?(?:0|84)(?:\d){9}$",
        message=_('Số điện thoại không hợp lệ.'))], null=True, blank=True)
    birth_day = models.DateField(_('Birth Day'), default=None, null=True)
    password = models.CharField(
        max_length=128, validators=[validate_password]
        #  Default password:12345@Qaz
        , default='pbkdf2_sha256$180000$8LyVdLFJgbEY$gCSdCqLYGy6qAOmMO4l5RkCBs/xLPsqI55RtQFDZhls='
        , help_text=password_validation.password_validators_help_text_html(), editable=False)
    is_superuser = models.BooleanField('Is Super Admin', default=True, editable=True)
    is_staff = models.BooleanField(default=True, editable=False)
    is_active = models.BooleanField('Active', default=True, help_text=_(
        'Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.'
    ))
    date_joined = models.DateField(_('Ngày tham gia'), default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True, editable=False)

    address = models.CharField(_('Địa chỉ'), max_length=255, null=True, blank=True)

    groups = models.ForeignKey(Group, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Vai trò'), default=5)

    centre = models.ForeignKey('centre.Centre', on_delete=models.PROTECT, verbose_name=_('Trung tâm'), default=None,
                               null=True, blank=True)

    user_permissions = models.ManyToManyField(
        Permission,
        blank=True, help_text=_('Specific permissions for this user.'),
        related_name='user_set',
        related_query_name='user',
        verbose_name='user permissions', editable=False,
        default=None)

    # created_user = models.ForeignKey('self', default=None, null=True, editable=False,
    #                                  on_delete=models.PROTECT, related_name='create_user_set')
    # updated_user = models.ForeignKey('self', default=None, null=True, editable=False,
    #                                  on_delete=models.PROTECT, related_name='update_user_set')
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'auth_user'
        verbose_name = _("Tài khoản người dùng")
        verbose_name_plural = _('Tài khoản người dùng')
        app_label = 'user'

    def __str__(self):
        return self.username

    def clean(self):
        if self.birth_day and self.birth_day >= date.today():
            raise ValidationError("Ngày sinh nhật phải là ngày hôm qua trở về trước")

    def get_centre_name(self):
        return self.centre.name

    centre_name = property(get_centre_name)


class AuthUserGroups(models.Model):
    authuser_id = models.IntegerField(blank=True, null=True)
    group_id = models.IntegerField(blank=True, null=True)
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='group_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='group_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'auth_user_groups'


class Student(models.Model):
    state = models.IntegerField(_('Trạng thái'), null=True, blank=True,
                                choices=[(1, 'Đang chờ lớp'), (2, 'Đang học'), (3, 'Hoàn thành'), (4, 'Bảo lưu'),
                                         (5, 'Mất cam kết'), (6, 'Thanh lý hợp đồng'), (7, 'Rút quyền lợi')], default=None)
    user = models.OneToOneField(AuthUser, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Thông tin cá nhân'), related_name='student_user_info_set')
    academic_power = models.IntegerField(_('Lực học'), null=True, blank=True,
                                         choices=[(1, 'Tốt'), (2, 'Khá'), (3, 'Trung bình'), (4, 'Yếu')], default=None)
    parents_phone = models.CharField(_('Số ĐT phụ huynh'), max_length=11, unique=False,
                                     default=None, null=True, blank=True,
                                     validators=[RegexValidator(
                                         regex="^\+?(?:0|84)(?:\d){9}$",
                                         message=_('Số điện thoại không hợp lệ.'))])
    current_company = models.CharField(_('Cơ quan/Trường học hiện tại'), max_length=255, null=True, blank=True)
    branch = models.CharField(_('Chuyên ngành'), max_length=255, null=True, blank=True)
    school_year = models.CharField(_('Niên khóa'), max_length=255, null=True, blank=True)
    learning_target = models.TextField(_('Mục tiêu học'), max_length=255, null=True, blank=True)
    learning_purpose = models.TextField(_('Mục đích học'), max_length=255, null=True, blank=True)
    free_to_test = models.CharField(_('Lịch dự kiến thi'), max_length=255, null=True, blank=True)
    free_to_learn = models.CharField(_('Lịch rảnh'), max_length=255, null=True, blank=True)
    how_to_know_odin = models.TextField(_('Bạn biết odin thông qua kênh nào?'), max_length=255, null=True, blank=True)
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='student_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=True,
                                     related_name='student_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'student'
        verbose_name = _("Học viên")
        verbose_name_plural = _('Học viên')
        app_label = 'user'

    def student_name(self):
        return self.user.full_name

    student_name.short_description = "Họ tên"
    student_name.admin_order_field = 'user'

    def __str__(self):
        return create_user_label(self.user.full_name, self.user.user_code)


class Teacher(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Thông tin cá nhân'))
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='teacher_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='teacher_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'teacher'
        verbose_name = _("Giáo viên")
        verbose_name_plural = _('Giáo viên')
        app_label = 'user'

    def centre(self):
        return self.user.centre.name

    def teacher_name(self):
        return self.user.full_name

    def __str__(self):
        return create_user_label(self.user.full_name, self.user.user_code)

    centre_name = property(centre)
    teacher_name.short_description = "Họ tên"
    teacher_name.admin_order_field = 'centre'
    centre.short_description = "Trung tâm"
    centre.admin_order_field = 'centre'


class Receptionist(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Thông tin cá nhân'))
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='receptionist_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='receptionist_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'receptionist'
        verbose_name = _("Lễ tân")
        verbose_name_plural = _('Lễ tân')
        app_label = 'user'

    def centre(self):
        return self.user.centre.name

    def reception_name(self):
        return self.user.full_name

    def __str__(self):
        return create_user_label(self.user.full_name, self.user.user_code)

    centre_name = property(centre)
    reception_name.short_description = "Họ tên"
    reception_name.admin_order_field = 'user'
    centre.short_description = "Trung tâm"
    centre.admin_order_field = 'centre'


class StudentCare(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.PROTECT,null=True, blank=True, verbose_name=_('Thông tin cá nhân'))
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='care_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='care_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'student_care'
        verbose_name = _("Chăm sóc học viên")
        verbose_name_plural = _('Chăm sóc học viên')
        app_label = 'user'

    def centre(self):
        return self.user.centre.name

    def student_care_name(self):
        return self.user.full_name

    def __str__(self):
        return create_user_label(self.user.full_name, self.user.user_code)

    student_care_name.short_description = "Tên"
    student_care_name.admin_order_field = "user"
    centre.short_description = "Trung tâm"
    centre.admin_order_field = "centre"


class BusinessEmployee(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.PROTECT,null=True, blank=True, verbose_name=_('Thông tin cá nhân'))
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='business_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='business_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'business_employee'
        verbose_name = _("Nhân viên kinh doanh")
        verbose_name_plural = _('Nhân viên kinh doanh')
        app_label = 'user'

    def centre(self):
        return self.user.centre.name

    def __str__(self):
        return create_user_label(self.user.full_name, self.user.user_code)

    centre.short_description = "Trung tâm"
    centre.admin_order_field = "centre"


class Commendation(models.Model):
    code = models.CharField(_('Mã khen thưởng'), unique=True, max_length=255, default=None)
    title = models.CharField(_('Tiêu đề'), max_length=255)
    students = models.ManyToManyField('user.Student', null=True, blank=True, verbose_name=_('Danh sách học viên'))
    centre = models.ForeignKey('centre.Centre', on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Trung tâm'), default=None)
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='commandation_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='commandation_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'commendation'
        verbose_name = _("Khen thưởng")
        verbose_name_plural = _('Khen thưởng')
        app_label = 'user'

    def __str__(self):
        return self.title


class CommendationStudent(models.Model):
    course = models.ForeignKey(Course, default=None, null=True, blank=True, verbose_name=_("Khóa học"), on_delete=models.PROTECT)
    commendation = models.ForeignKey(Commendation, null=True, blank=True, verbose_name=_("Khen thưởng"), on_delete=models.PROTECT)
    student = models.ForeignKey('user.Student', default=None, null=True, blank=True, verbose_name=_("Học viên"), on_delete=models.PROTECT)
    note = models.CharField(_("Ghi chú"), max_length=255, default=None, null=True, blank=True)

    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='comm_student_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='comm_student_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'commendation_student'
        verbose_name = _("Khen thưởng học viên")
        verbose_name_plural = _('Khen thưởng học viên')
        app_label = 'user'


class Tests(models.Model):
    classes = models.ForeignKey(Classes, null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('Lớp học'), default=None)
    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    level = models.IntegerField(_('Mức độ'), null=True, blank=True,
                                choices=[(1, 'Cơ bản'), (2, 'Trung cấp'), (3, 'Nâng cao'), (4, 'Cao cấp')],
                                default=None)
    test_date = models.DateField(_('Ngày diễn ra'), default=None)
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='tests_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='tests_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'tests'
        verbose_name = _("Kết quả test")
        verbose_name_plural = _('Kết quả test')
        app_label = 'user'

    def __str__(self):
        return self.title

    def get_test_result(self):
        return StudentTestResult.objects.filter(test_id=self.id)

    test_result = property(get_test_result)


class StudentTestResult(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Khóa học'), default=None)
    classes = models.ForeignKey(Classes, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Lớp học'), default=None)
    student = models.ForeignKey('user.Student', on_delete=models.PROTECT, null=True, blank=True, default=None, verbose_name=_("Sinh viên"))
    test = models.ForeignKey(Tests, on_delete=models.PROTECT, default=None, null=True, blank=True, verbose_name=_("Bài test"))
    point = models.IntegerField(_("Điểm"), validators=[MaxValueValidator(10), MinValueValidator(0)], default=None,
                                null=True)
    note = models.CharField(_("Ghi chú"), max_length=255, default=None, null=True, blank=True)
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='test_result_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='test_result_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'student_test_result'
        verbose_name = _("Kết quả test")
        verbose_name_plural = _('Kết quả test')
        app_label = 'centre'

    def __str__(self):
        return 'Học viên ' + self.student.student_name()


class StudentCallHistory(models.Model):
    student = models.ForeignKey('user.Student', null=True, blank=True, on_delete=models.PROTECT, default=None, verbose_name=_("Sinh viên"))
    note = models.CharField(_("Ghi chú"), max_length=255, default=None, null=True, blank=True)
    call_user = models.ForeignKey(StudentCare, default=None, null=True, blank=True,
                                  verbose_name=_("CSHV gọi"), on_delete=models.PROTECT)
    call_date = models.DateField(_("Ngày gọi"), null=True, default=timezone.now, blank=True)
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False,
                                     related_name='student_call_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='student_call_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'student_call_history'
        verbose_name = _("Lịch sử gọi sinh viên")
        verbose_name_plural = _('Lịch sử gọi sinh viên')
        app_label = 'user'

