from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from manager.constant import STUDY_SHIFT_CHOICES


class Revenue(models.Model):
    title = models.CharField(_('Tiêu đề'), max_length=255)
    centre = models.ForeignKey('centre.Centre', null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('Trung tâm'), default=None)
    user = models.OneToOneField('user.AuthUser', null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('Người nộp'),
                                 default=None)
    amount = models.IntegerField(_('Số tiền (VNĐ)'), validators=[MinValueValidator(0)])
    input_date = models.DateField(_('Ngày thu'), default=None)
    note = models.CharField(_("Ghi chú"), max_length=255, default=None, null=True, blank=True)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='revenue_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='revenue_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'revenues'
        verbose_name = _("Doanh thu")
        verbose_name_plural = _('Doanh thu')
        app_label = 'finance'

    def __str__(self):
        return self.title


class StudentDebt(models.Model):
    centre = models.ForeignKey('centre.Centre', on_delete=models.PROTECT, verbose_name=_('Trung tâm'), default=None, null=True, blank=True)
    title = models.CharField(_('Mã người giới thiệu'), max_length=255, default=None,null=True, blank=True)
    student = models.ForeignKey('user.Student', on_delete=models.PROTECT, verbose_name=_('Học viên'))
    reward = models.ForeignKey('finance.Reward', on_delete=models.PROTECT, verbose_name=_('Ưu đãi'), default=None, null=True, blank=True)
    student_level = models.IntegerField(_('Trình độ hiện tại'), null=True, blank=True,
                                        choices=[(1, 'Cơ bản '),
                                                 (2, 'Đã học qua Python Core'),
                                                 (3, 'Đã học qua Java Core'),
                                                ], default=None)
    # student_state = models.IntegerField(_('Trạng thái HV'), null=True, blank=True,
    #                                     choices=[(1, 'Xếp lớp'),
    #                                              (2, 'Nhận lớp'),
    #                                              (3, 'Bảo lưu'),
    #                                              (4, 'Tốt nghiệp'),
    #                                              (5, 'Rút quyền lợi')], default=None)
    course = models.ForeignKey('centre.Course', null=True, blank=True, verbose_name=_('Khóa học'), on_delete=models.PROTECT, default=None)
    study_schedule_select = models.IntegerField(_('Ca học'), default=1, choices=STUDY_SHIFT_CHOICES)
    origin_amount = models.IntegerField(_('Giá'), validators=[MinValueValidator(0)], default=0, null=True, blank=True)
    discount_percent = models.IntegerField(_('Giảm giá(%)'), validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         default=0, editable=False)
    plan_date = models.DateField(_('Ngày hẹn hoàn thành'), default=None)
    rest_amount = models.IntegerField(_('Số tiền còn nợ'), default=0, validators=[MinValueValidator(0)]
                                      , help_text=""
                                      , null=True, blank=True)
    back_amount = models.IntegerField(_('Số tiền hoàn lại'), default=0, validators=[MinValueValidator(0)],
                                      null=True, blank=True)
    back_reason = models.CharField(_('Lý do hoàn lại'), max_length=255, default=None, null=True, blank=True)
    completed_pay_date = models.DateField(_('Ngày hoàn thành'), null=True, blank=True)
    gift = models.CharField(_('Quà tặng'), max_length=255, default=None, null=True, blank=True)
    counselor = models.ForeignKey('user.AuthUser', on_delete=models.PROTECT, related_name="counselor_set",
                                  verbose_name=_('Nhân viên kinh doanh'), default=None, null=True, blank=True)
    collector = models.ForeignKey('user.AuthUser', on_delete=models.PROTECT, related_name="collector_set",
                                  verbose_name=_('Người thu'), default=None, null=True, blank=True)
    consultant = models.CharField(_('Tư vấn viên'), max_length=255, default=None, null=True, blank=True)
    contract = models.CharField(_('Hợp đồng'), max_length=255, default=None, null=True, blank=True)
    receipt = models.CharField(_('Hóa đơn'), max_length=255, default=None, null=True, blank=True)
    contract_state = models.IntegerField(_('Tình trạng hợp đồng'), null=True, blank=True,
                                        choices=[(1, 'Cam kết'),
                                                 (2, 'Mất cam kết'),
                                                 (3, 'Cảnh cáo'),
                                                 (4, 'Thanh lý hợp đồng')], default=None)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='studentdebt_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='studentdebt_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'student_debt'
        verbose_name = _("Doanh thu")
        verbose_name_plural = _('Doanh thu')
        app_label = 'finance'

    def __str__(self):
        return self.title

    def student_name(self):
        return self.student.student_name

    student_name.short_description = 'Học viên'

    # def clean(self):
    #     must_pay_amount = (1 - self.discount_percent / 100) * self.origin_amount
    #     sum_paid_amount = Payment.objects.filter(student_debt_id=self.id).aggregate(Sum('paid_amount'))['paid_amount__sum']
    #     if sum_paid_amount and 0 < must_pay_amount < sum_paid_amount:
    #         raise ValidationError('Tổng số tiền các lần nộp vượt quá tổng số tiền phải nộp.')


class Payment(models.Model):
    student_debt = models.ForeignKey(StudentDebt, null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('Công nợ'))
    paid_amount = models.IntegerField(_('Số tiền'), default=0, validators=[MinValueValidator(0)])
    payment_method = models.IntegerField(_('Tài khoản nộp'), null=True, blank=True,
                                           choices=[(0, 'Tiền mặt'), (1, 'Tech'), (2, 'MB'), (3, 'BIDV')], default=None)
    completed_pay_date = models.DateField(_('Ngày nộp'), default=timezone.now())

    class Meta:
        managed = True
        db_table = 'payment'
        verbose_name = _("Thanh toán công nợ")
        verbose_name_plural = _('Thanh toán công nợ')
        app_label = 'finance'


class StudentSendPaymentRequest(models.Model):
    title = models.CharField(_('Tiêu đề'), max_length=255)
    transaction_id = models.CharField(_('Mã giao dịch'), max_length=255, null=True, blank=True)
    centre = models.ForeignKey('centre.Centre', null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('Trung tâm'), default=None)
    full_name = models.CharField(_('Tên sinh viên'), max_length=150, default=None)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=11, default=None,
                             validators=[
                                 RegexValidator(regex="^\+?(?:0|84)(?:\d){9}$",
                                                message=_('Số điện thoại không hợp lệ.'))], null=True)
    address = models.CharField(_('Địa chỉ'), max_length=255, null=True, blank=True)
    course = models.ForeignKey('centre.Course', null=True, blank=True, verbose_name=_('Khóa học'), on_delete=models.PROTECT, default=None)
    classes = models.ForeignKey('centre.Classes', verbose_name=_('Lớp học'), on_delete=models.PROTECT, default=None, null=True, blank=True)
    study_schedule_select = models.IntegerField(_('Ca học'), default=1, choices=STUDY_SHIFT_CHOICES)
    reward = models.ForeignKey('finance.Reward', on_delete=models.PROTECT, verbose_name=_('Ưu đãi'), null=True, blank=True, default=None)
    must_pay_amount = models.IntegerField(_('Số tiền phải nộp'), default=0, validators=[MinValueValidator(0)])
    paid_amount = models.IntegerField(_('Số tiền nộp'), default=0, validators=[MinValueValidator(0)])
    payment_method = models.IntegerField(_('Tài khoản nộp'), null=True, blank=True,
                                         choices=[(0, 'Tiền mặt'), (1, 'Tech'), (2, 'MB'), (3, 'BIDV')], default=None)
    state = models.IntegerField(_('Trạng thái'), null=True, blank=True,
                                choices=[(1, 'Đồng ý'), (2, 'Chờ HV'), (3, 'Từ chối')], default=None)
    send_date = models.DateField(_('Ngày nộp'), default=timezone.now())
    plan_complete_date = models.DateField(_('Ngày hen hoan thanh'), default=None, null=True, blank=True)
    student_level = models.IntegerField(_('Trình độ hiện tại'), null=True, blank=True,
                                        choices=[(1, 'BB'),
                                                 (2, 'C'),
                                                 (3, 'IE1'),
                                                 (4, 'IE2'),
                                                 (5, 'IE3'),
                                                 (6, 'TO1'),
                                                 (7, 'TO2')], default=None)
    free_day_in_week = models.CharField(_('Lịch rảnh'), max_length=255, null=True, blank=True)
    student_debt = models.ForeignKey(StudentDebt, on_delete=models.CASCADE,
                                        default=None, null=True, blank=True, editable=False)

    class Meta:
        managed = True
        db_table = 'student_send_request_payment'
        verbose_name = _("Thanh toán học phí")
        verbose_name_plural = _('Thanh toán học phí')
        app_label = 'finance'

    def __str__(self):
        return self.title


class StudentDebtView(models.Model):
    class Meta:
        managed = True
        verbose_name = _("HV đến hạn nộp tiền")
        verbose_name_plural = _('HV đến hạn nộp tiền')
        app_label = 'finance'

    def __str__(self):
        return "Danh sách HV hết hạn nộp tiền"


class Reward(models.Model):
    title = models.CharField(_('Tiêu đề'), max_length=255)
    code = models.CharField(_('Mã ưu đãi'), max_length=255, unique=True)
    course = models.ManyToManyField('centre.Course',
                               help_text=_('Nếu không trọn khoá học nào, ưu đãi sẽ được áp dụng cho tất cả các khoá học.<br>'),
                               verbose_name=_('Khóa học'), default=None, null=True, blank=True)
    type = models.IntegerField(_('Loại ưu đãi'), default=1, choices=[(1, 'Giảm giá'), (2, 'Quà tặng')])
    quantity = models.IntegerField(_('Số lượng'), default=0, validators=[MinValueValidator(0)])
    gift = models.CharField(_('Quà tặng'), max_length=255, null=True, blank=True)
    discount_percent = models.IntegerField(_('Giảm giá (%)'), default=0, validators=[MinValueValidator(0)])
    start_date = models.DateField(_('Ngày bắt đầu'), default=date.today())
    end_date = models.DateField(_('Ngày kết thúc'), default=date.today() + timedelta(days=30))

    class Meta:
        managed = True
        db_table = 'reward'
        verbose_name = _("Ưu đãi")
        verbose_name_plural = _('Ưu đãi')
        app_label = 'finance'

    def __str__(self):
        return self.code

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('Ngày bắt đầu phải trước ngày kết thúc')



# class StudentReceiveReward(models.Model):
#     student = models.ForeignKey('user.Student', on_delete=models.PROTECT, verbose_name=_('Học viên'))
#     reward = models.ForeignKey('finance.Reward', on_delete=models.PROTECT, verbose_name=_('Ưu đãi'))
#
#     class Meta:
#         managed = True
#         db_table = 'student_receive_reward'
#         verbose_name = _("HV nhận ưu đãi")
#         verbose_name_plural = _('HV nhận ưu đãi')
#         app_label = 'finance'
