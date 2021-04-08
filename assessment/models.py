from django.db import models
from django.utils.translation import gettext as _

from user.models import AuthUser


class AssessmentCategory(models.Model):
    code = models.CharField(_("Mã đánh giá"), max_length=10, default=None, null=True, blank=True)
    content = models.CharField(_("Nội dung"), max_length=255, default=None, null=True, blank=True)
    type = models.IntegerField(_("Phân loại"),
                               choices=[(1, 'Đánh giá giáo viên theo buổi học')
                                        , (2, 'Đánh giá học viên theo khóa học')
                                        , (3, 'Đánh giá sinh viên theo buổi học')
                                        , (4, 'Đánh giá học viên theo khóa học')
                                        , (5, 'Đánh giá tổ chức khóa học')
                                        , (6, 'Khảo sát độ hài lòng')

                                        ],
                                            default=None, null=True, blank=True)

    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='assessment_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='assessment_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    updated_date_time = models.DateTimeField(null=True, auto_now=True, editable=False)

    class Meta:
        managed = True
        db_table = 'assessment_category'
        verbose_name = _("Danh mục đánh giá")
        verbose_name_plural = _('Danh mục đánh giá')
        app_label = 'assessment'


class CourseOrganizeAssessment(models.Model):
    course = models.ManyToManyField('centre.Course', default=None, null=True, blank=True, verbose_name=_("Khóa học"))
    assessment_category = models.IntegerField(_('Danh mục đánh giá'), default=None,
                                              choices=[(1, 'Thái độ của nhân viên tại Odin'),
                                                       (2, 'Cơ sở vật chất(trang thiết bị giảng dạy, phòng học...)'
                                                           ' của Học viện Odin'),
                                                       (
                                                           3,
                                                           'Những ý kiến đóng góp dành cho chất lượng dịch vụ của Odin'),
                                                       ])
    assessment = models.IntegerField(_("Đánh giá"), choices=[(1, 'Tốt'), (2, 'Khá'),
                                                             (3, 'Trung bình'), (4, 'Kém')],
                                     default=None, null=True, blank=True)
    explain = models.CharField(_("Giải thích"), max_length=255, default=None, null=True, blank=True)
    assessment_create_user = models.ManyToManyField('user.AuthUser', null=True, blank=True, verbose_name=_('Người đánh giá'), default=None)
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='course_orz_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='course_orz_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    updated_date_time = models.DateTimeField(null=True, auto_now=True, editable=False)

    class Meta:
        managed = True
        db_table = 'course_organize_assessment'
        verbose_name = _("Đánh giá tổ chức khóa học")
        verbose_name_plural = _('Đánh giá tổ chức khóa học')
        app_label = 'assessment'


class CourseSatisfiedAssessment(models.Model):
    course = models.ManyToManyField('centre.Course', default=None, null=True, blank=True, verbose_name=_("Khóa học"))
    assessment = models.IntegerField(_("Đánh giá"), choices=[(1, 'Rất hài lòng'), (2, 'Hài lòng'),
                                                             (3, 'Tạm được'), (4, 'Chán'), (5, 'Rất chán')],
                                     default=None, null=True, blank=True)
    explain = models.CharField(_("Giải thích"), max_length=255, default=None, null=True, blank=True)
    assessment_create_user = models.ManyToManyField('user.AuthUser', null=True, blank=True, verbose_name=_('Người đánh giá'), default=None)
    created_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, related_name='course_satisfied_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey(AuthUser, default=None, null=True, blank=True, editable=False, related_name='course_satisfied_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    updated_date_time = models.DateTimeField(null=True, auto_now=True, editable=False)

    class Meta:
        managed = True
        db_table = 'course_satisfied_assessment'
        verbose_name = _("Độ hài lòng về khóa học")
        verbose_name_plural = _('Độ hài lòng về khóa học')
        app_label = 'assessment'
