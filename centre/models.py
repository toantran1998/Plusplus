from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from finance.models import StudentDebt
from manager.constant import STUDY_SHIFT_CHOICES


class Centre(models.Model):
    name = models.CharField(_('name'), max_length=255, default=None, unique=True)
    address = models.CharField(_('address'), max_length=255, default=None)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='centre_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, blank=True, null=True, editable=False, related_name='centre_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    updated_date_time = models.DateTimeField(null=True, auto_now=True, editable=False)

    class Meta:
        managed = True
        db_table = 'centre'
        verbose_name = _("Trung tâm")
        verbose_name_plural = _('Trung tâm')
        app_label = 'centre'

    def __str__(self):
        return self.name

    @property
    def count(self):
        return self.objects.count()


class ClassRoom(models.Model):
    centre = models.ForeignKey(Centre, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Trung tâm'), default=None)
    class_room_code = models.CharField(_('Mã phòng học'), max_length=10, default=None, unique=True)
    name = models.CharField(_('Tên phòng học'), max_length=255)
    address = models.CharField(_('Địa chỉ'), max_length=255)
    size = models.IntegerField(_('Số ghế'), null=True, default=0, validators=[MinValueValidator(1)])
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='classroom_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='classroom_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'class_room'
        verbose_name = _("Phòng học")
        verbose_name_plural = _('Phòng học')
        app_label = 'centre'

    def __str__(self):
        return self.name


class Course(models.Model):
    code = models.CharField(_('Mã khóa học'), unique=True, max_length=255, default=None)
    name = models.CharField(_('Tên khóa học'), max_length=255)
    cost = models.IntegerField(verbose_name=_('Giá gốc'), default=0, validators=[MinValueValidator(1)])
    night_cost = models.IntegerField(verbose_name=_('Giá ca ngày'), default=0, validators=[MinValueValidator(1)])
    daytime_cost = models.IntegerField(verbose_name=_('Giá ca tối'), default=0, validators=[MinValueValidator(1)])
    # discount_percent = models.IntegerField(_('Giảm giá(%)'), validators=[MinValueValidator(0), MaxValueValidator(100)],
    #                                        default=0)
    study_shift_count = models.IntegerField(verbose_name=_('Số buổi học'), default=0, validators=[MinValueValidator(1)])
    description = models.CharField(_('Mô tả'), max_length=255, default=None, null=True, blank=True)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='course_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='course_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    updated_date_time = models.DateTimeField(null=True, auto_now=True, editable=False)

    class Meta:
        managed = True
        db_table = 'course'
        verbose_name = _("Bảng giá")
        verbose_name_plural = _('Bảng giá')
        app_label = 'centre'

    def __str__(self):
        return self.name


class Classes(models.Model):
    centre = models.ForeignKey('centre.Centre', on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Trung tâm'), default=None)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Khóa học'), default=None)
    code = models.CharField(_('Mã lớp học'), max_length=255, unique=True, default=None, null=True, blank=True)
    name = models.CharField(_('Tên lớp học'), max_length=255)
    day_in_week = models.IntegerField(_('Lịch học'), choices=[(1, 'Thứ 2-5'), (2, 'Thứ 3-6'), (3, 'Thứ 4-7')], default=None)
    start_date = models.DateField(_('Ngày khai giảng'), null=True, default=None)
    study_shift_select = models.IntegerField(_('Ca học'), default=None, choices=STUDY_SHIFT_CHOICES)
    end_date = models.DateField(_('Ngày kết thúc'), default=None, null=True, blank=True)
    classes_order_no = models.IntegerField(default=0, editable=False)
    waiting_flag = models.BooleanField(_('Lớp chờ'), default=False)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='classes_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='classes_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(_('Ngày tạo'), null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'classes'
        verbose_name = _("Lớp học")
        verbose_name_plural = _('Lớp học')
        app_label = 'centre'
        ordering = ['-waiting_flag']

    def __str__(self):
        return self.name

    @property
    def count_study_shift(self):
        return StudyShift.objects.filter(classes=self).count()


class ClassesStudents(models.Model):
    student_debt = models.ForeignKey(StudentDebt, null=True, blank=True, verbose_name=_('Công nợ'), on_delete=models.PROTECT, default=None)
    classes = models.ForeignKey(Classes, default=None, null=True, blank=True, verbose_name=_("Lớp học"), on_delete=models.PROTECT)
    next_course_code = models.CharField(_('Mã khóa tiếp theo'), null=True, blank=True, default=None,
                                        editable=False, max_length=255)
    student = models.ForeignKey('user.Student', default=None, null=True, blank=True, verbose_name=_("Học viên"), on_delete=models.CASCADE)
    study_start_date = models.DateField(null=True, editable=False)
    note = models.CharField(_("Ghi chú"), max_length=255, default=None, null=True, blank=True)
    commitment = models.CharField(_("Cam kết"), max_length=255, default=None, null=True, blank=True)
    assessment = models.CharField(_("Đánh giá"), max_length=255, default=None, null=True, blank=True)
    state = models.IntegerField(_('Trạng thái'), null=True, blank=True,
                                choices=[(1, 'Chờ xếp lớp'),
                                         (2, 'Đã nhận lớp'),
                                         (3, 'Tốt nghiệp'),
                                         (4, 'Bảo lưu (1 tháng)'),
                                         (5, 'Bảo lưu (6 tháng)'),
                                         (6, 'Rút quyền'),
                                         (7, 'Hủy')], default=1)
    added_study_shift = models.BooleanField(_('Đã thêm vào buổi học'), default=False)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True,
                                     related_name='classes_student_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False,
                                     related_name='classes_student_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'classes_student'
        app_label = 'centre'

    # def __str__(self):
    #     return self.student.user.user_code


class ClassesTeachers(models.Model):
    # course = models.ManyToManyField(Course, verbose_name=_('Khóa học'))
    classes = models.ForeignKey(Classes, default=None, verbose_name=_("Lớp học"), null=True, blank=True, on_delete=models.PROTECT)
    teacher = models.ForeignKey('user.Teacher', default=None, null=True, blank=True, verbose_name=_("Giáo viên"), on_delete=models.PROTECT)
    assessment = models.CharField(_("Đánh giá"), max_length=255, default=None, null=True, blank=True)
    note = models.CharField(_("Ghi chú"), max_length=255, default=None, null=True, blank=True)
    added_study_shift = models.BooleanField(_('Đã thêm vào buổi học'), default=False)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='classes_teacher_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='classes_teacher_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'classes_teacher'
        app_label = 'centre'


class Issues(models.Model):
    centre = models.ForeignKey('centre.Centre', null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('Trung tâm'), default=None)
    classes = models.ForeignKey('centre.Classes', null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('Lớp học'), default=None)
    title = models.CharField(_("Tiêu đề"), max_length=255, default=None, null=True, blank=True)
    content = models.TextField(_("Nội dung"), max_length=255, default=None, null=True, blank=True)
    student = models.ForeignKey('user.Student', default=None, null=True, blank=True, verbose_name=_("Học viên"), on_delete=models.CASCADE)

    category = models.IntegerField(_("Phân loại"), choices=[(1, 'Bảo hành')
                                   , (2, 'Bảo lưu')
                                   , (3, 'Hỗ trợ học tập')
                                   , (4, 'Khiếu nại')
                                   , (5, 'Rút quyền lợi')
                                   , (6, 'Khác')], default=None, null=True, blank=True)
    state = models.IntegerField(_("Trạng thái"), choices=[(1, 'Chờ xử lý')
                                       , (2, 'Đang xử lý')
                                       , (3, 'Hoàn thành')
                                       , (4, 'Huỷ')], default=None, null=True, blank=True)
    call_user = models.ForeignKey("user.StudentCare", default=None, null=True, blank=True,
                                  verbose_name=_("CSHV gọi"), on_delete=models.PROTECT)
    call_date = models.DateField(_('Ngày gọi'), default=timezone.now())
    created_user = models.ForeignKey("user.AuthUser", default=None, null=True, blank=True, related_name='issues_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey("user.AuthUser", default=None, null=True, blank=True, editable=False, related_name='issues_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    updated_date_time = models.DateTimeField(null=True, auto_now=True, editable=False)

    class Meta:
        managed = True
        db_table = 'issues'
        verbose_name = _("Issues")
        verbose_name_plural = _('Quản lý Issues')
        app_label = 'centre'


class StudyShift(models.Model):
    classes = models.ForeignKey(Classes, default=None, verbose_name=_("Lớp học"), on_delete=models.PROTECT, null=True, blank=True)
    class_room = models.ForeignKey(ClassRoom, default=None, verbose_name=_("Phòng học"), null=True, blank=True,
                                   on_delete=models.PROTECT)
    order_no = models.IntegerField(_('STT buổi'), default=None)
    main_content = models.TextField(_('Nội dung chính'), null=True, blank=True)
    session_date = models.DateField(_('Ngày diễn ra'), default=None)
    from_time = models.TimeField(_('Thời gian bắt đầu'), default=None)
    to_time = models.TimeField(_('Thời gian kết thúc'), default=None)
    home_work_content = models.TextField(_('Nội dung BTVN'), null=True, blank=True)
    study_shift_select = models.IntegerField(_('Ca học'), null=True, blank=True, default=None,
                                             choices=STUDY_SHIFT_CHOICES)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='study_shift_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='study_shift_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'study_shift'
        verbose_name = _("Buổi học")
        verbose_name_plural = _('Buổi học')
        app_label = 'centre'

    def __str__(self):
        return 'Buổi %s' % self.order_no

    def clean(self):
        if self.from_time and self.to_time and self.from_time > self.to_time:
            raise ValidationError('Thời gian bắt đầu phải trước thời gian kết thúc')

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))


class FeedBackTeachingQuality(models.Model):
    STUDENT_FEEDBACK_CATEGORIES = [(1, 'Sử dụng công cụ hỗ trợ (hình ảnh/video) hiệu quả'),
                                   (2, 'Giọng nói lưu loát, rõ ràng'),
                                   (3, 'Truyền năng lượng tốt trong lớp học'),
                                   (4, 'Hướng dẫn HV một cách dễ hiểu và rõ ràng'),
                                   (5, 'Tổng hợp và nhấn mạnh các nội dung chính của bài'),
                                   (6, 'Đưa ra câu hỏi và tương tác với HV'),
                                   (7, 'Quan tâm và chữa lỗi cho học viên với câu trả lời sai'),
                                   (8, 'Hỗ trợ và hướng dẫn HV khi gặp khó khăn'),
                                   (9, 'Khuyến khích HV trong quá trình học'),
                                   (10, 'Giao nhiệm vụ phù hợp với trình độ của HV'),
                                   (11, 'Ưu điểm'),
                                   (12, 'Nhược điểm')]

    GSHT_FEEDBACK_CATEGORIES = [(13, 'Handout phù hợp với buổi học và mang tính sáng tạo'),
                                (14, 'Kiểm soát được tốc độ bài giảng'),
                                (15, 'Sử dụng tốt ngôn ngữ hình thể'),
                                (16, 'Nội dung bài giảng sát với kết hoạch giảng dạy'),
                                (17, 'Khiến học viên tham gia nhiệt tình và tập trung vào bài giảng'),
                                (18, 'Trừ số điểm chất lượng giảng dạy')]

    study_shift = models.ForeignKey(StudyShift, verbose_name=_("Buổi học"), on_delete=models.PROTECT, null=True, blank=True)
    teacher = models.ManyToManyField('user.Teacher', default=None, verbose_name=_("Giáo viên"), null=True, blank=True)
    assessment_category = models.IntegerField(_('Danh mục đánh giá'), default=None, null=True, blank=True,
                                              choices=STUDENT_FEEDBACK_CATEGORIES)
    assessment = models.CharField(_("Đánh giá"), max_length=255, default=None, null=True, blank=True)
    explain = models.CharField(_("Giải thích"), max_length=255, default=None, null=True, blank=True)
    assessment_create_user = models.ManyToManyField('user.AuthUser', null=True, blank=True, verbose_name=_('Người đánh giá'), default=None)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='feedback_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='feedback_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'feed_back_teaching_quality'
        verbose_name = _("Đánh giá chất lượng giảng dạy")
        verbose_name_plural = _('Đánh giá chất lượng giảng dạy')
        app_label = 'centre'


class StudyShiftStudent(models.Model):
    # course = models.ForeignKey(Course, default=None, verbose_name=_("Khóa học"), ons_delete=models.PROTECT)
    # classes = models.ForeignKey(Classes, default=None, verbose_name=_("Lớp học"), on_delete=models.PROTECT)
    study_shift = models.ForeignKey(StudyShift, null=True, blank=True, verbose_name=_("Buổi học"), on_delete=models.PROTECT)
    student = models.ForeignKey('user.Student', default=None, null=True, blank=True, verbose_name=_("Học viên"), on_delete=models.PROTECT)
    attendance = models.BooleanField(_('Điểm danh'), default=False)
    leave_request = models.BooleanField(_('Nghỉ có phép'), default=False)
    assessment = models.CharField(_("Đánh giá"), max_length=255, default=None, null=True, blank=True)
    home_work = models.BooleanField(_('BTVN'), default=False)
    note = models.CharField(_("Ghi chú"), max_length=255, default=None, null=True, blank=True)
    # state = models.IntegerField(_('Trạng thái'), default=None,
    #                             choices=[(1, 'Handout phù hợp với buổi học và mang tính sáng tạo'),
    #                             (2, 'Kiểm soát được tốc độ bài giảng'),
    #                             (3, 'Sử dụng tốt ngôn ngữ hình thể'),
    #                             (4, 'Nội dung bài giảng sát với kết hoạch giảng dạy'),
    #                             (5, 'Khiến học viên tham gia nhiệt tình và tập trung vào bài giảng'),
    #                             (6, 'Trừ số điểm chất lượng giảng dạy')])
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='shift_student_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='shift_student_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'study_shift_student'
        verbose_name = _("Điểm danh học viên")
        verbose_name_plural = _('Điểm danh học viên')
        app_label = 'centre'


class StudyShiftTeacher(models.Model):
    # course = models.ForeignKey(Course, default=None, verbose_name=_("Khóa học"), on_delete=models.PROTECT)
    # classes = models.ForeignKey(Classes, default=None, verbose_name=_("Lớp học"), on_delete=models.PROTECT)
    study_shift = models.ForeignKey(StudyShift, null=True, blank=True, verbose_name=_("Buổi học"), on_delete=models.PROTECT)
    teacher = models.ForeignKey('user.Teacher', default=None, null=True, blank=True, verbose_name=_("Giáo viên"), on_delete=models.PROTECT)
    assessment_category = models.IntegerField(_('Danh mục đánh giá'), default=None, null=True, blank=True,
                                              choices=[(1, 'Trang phục'),
                                                       (2, 'Đến lớp đúng giờ'),
                                                       (3, 'Hoàn thành sổ đầu bài'),
                                                       (4, 'Giữ gìn cơ sở vật chất'),
                                                       (5, 'Bàn giao đầy đủ trang thiết bị'),
                                                       (6, 'Gửi handout đúng giờ & đúng tiêu đề'),
                                                       (7, 'Khác'),
                                                       ])
    assessment = models.BooleanField(_("Đánh giá"), default=False)
    explain = models.CharField(_("Giải thích"), max_length=255, default=None, null=True, blank=True)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='shift_teacher_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='shift_teacher_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'study_shift_teacher'
        verbose_name = _("Đánh giá giáo viên")
        verbose_name_plural = _('Đánh giá giáo viên')
        app_label = 'centre'


class CourseSurvey(models.Model):
    course = models.ManyToManyField(Course, default=None, null=True, blank=True, verbose_name=_("Khóa học"))
    teacher = models.ManyToManyField('user.Teacher', default=None, null=True, blank=True, verbose_name=_("Giáo viên"))
    assessment_category = models.IntegerField(_('Danh mục đánh giá'), default=None,
                                              choices=[(1, 'Kiến thức chuyên môn'),
                                                       (2, 'Kỹ năng truyền dạt(diễn đạt rõ ràng, sinh động...)'),
                                                       (3, 'Phương pháp giảng dạy (thảo luận, chuẩn bị tài liệu...)'),
                                                       (4, 'Những ý kiến góp ý/ đánh giá khác dành cho Giáo '
                                                           'viên để nâng cao chất lượng giảng dạy'),
                                                       ])
    assessment = models.IntegerField(_("Đánh giá"), choices=[(1, 'Tốt'), (2, 'Khá'),
                                                             (3, 'Trung bình'), (4, 'Kém')],
                                     default=1, null=True, blank=True)
    explain = models.CharField(_("Giải thích"), max_length=255, default=None, null=True, blank=True)
    assessment_create_user = models.ManyToManyField('user.AuthUser', null=True, blank=True, verbose_name=_('Người đánh giá'), default=None)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='survey_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='survey_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'course_survey'
        verbose_name = _("Khảo sát khóa học")
        verbose_name_plural = _('Khảo sát khóa học')
        app_label = 'centre'


class CourseTeacherAssessment(models.Model):
    course = models.ManyToManyField(Course, default=None, null=True, blank=True, verbose_name=_("Khóa học"))
    assessment_category = models.IntegerField(_('Danh mục đánh giá'), default=None,
                                              choices=[(1, 'Bạn biết đến Khóa học của Odin qua kênh tư vấn nào:'),
                                                       (2, 'Bạn có cảm nhận sự khác biệt về trải nghiệm khóa học'
                                                           ' so với thông tư vấn ban đầu hay không?'),
                                                       (3, 'Khóa học liên quan tới công việc/ việc học của bạn ở'
                                                           ' mức độ nào?'),
                                                       (4, 'Khóa học có đạt được tính ứng dụng cao?'),
                                                       (5, 'Tôi có thể áp dụng khóa học này dễ dàng hơn nếu nội'
                                                           ' dung được cải tiến'),
                                                       ])
    assessment = models.IntegerField(_("Đánh giá"), choices=[(1, 'Tốt'), (2, 'Khá'),
                                                             (3, 'Trung bình'), (4, 'Kém')],
                                     default=None, null=True, blank=True)
    explain = models.CharField(_("Giải thích"), max_length=255, default=None, null=True, blank=True)
    assessment_create_user = models.ManyToManyField('user.AuthUser', null=True, blank=True, verbose_name=_('Người đánh giá'), default=None)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='course_teacher_ass_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='course_teacher_ass_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'course_teacher_assessment'
        verbose_name = _("Đánh giá giáo viên")
        verbose_name_plural = _('Đánh giá giáo viên')
        app_label = 'centre'


class Tasks(models.Model):
    # def student_off_yesterday(self):
    #     return Student.objects.filter(state=5) \
    #         .annotate(student_off_yesterday=F("user__full_name")).values("student_off_yesterday")
    # student_off_yesterday.short_description = "HV nghỉ hôm trước"

    class Meta:
        managed = False
        verbose_name = _("Việc cần làm")
        verbose_name_plural = _('Việc cần làm')
        app_label = 'centre'


class StudentOffYesterday(models.Model):
    class Meta:
        managed = False
        verbose_name = _("HV nghỉ hôm qua")
        verbose_name_plural = _('HV nghỉ hôm qua')
        app_label = 'centre'


class StudentOffFromTwoDays(models.Model):
    class Meta:
        managed = False
        verbose_name = _("HV nghỉ nhiều")
        verbose_name_plural = _('HV nghỉ nhiều')
        app_label = 'centre'


class StudentLostConfirm(models.Model):
    class Meta:
        managed = False
        verbose_name = _("HV mất cam kết")
        verbose_name_plural = _('HV mất cam kết')
        app_label = 'centre'


class StudyShiftSchedule(models.Model):
    class Meta:
        managed = False
        verbose_name = _("Lịch học")
        verbose_name_plural = _('Lịch học')
        app_label = 'centre'
