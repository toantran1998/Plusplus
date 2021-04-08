from datetime import date

from django import forms
from django.core.validators import RegexValidator
from django.db.models import Q
from django.utils.translation import gettext as _

from app_config.settings import DEFAULT_DATE_FORMAT
from centre.models import Centre, Course, Classes
from finance.models import Reward, StudentDebt, StudentSendPaymentRequest
from manager.constant import STUDY_SHIFT_CHOICES
from user.models import AuthUser

CENTRE_CHOICE_EMPTY = [('', '---Chọn trung tâm---')]
COURSE_CHOICE_EMPTY = [('', '---Chọn khoá học---')]
COURSE_CLASSES_EMPTY = [('', '---Chọn lớp học---')]


class RegistrationForm(forms.Form):
    try:
        CENTRE_CHOICES = (CENTRE_CHOICE_EMPTY + list(Centre.objects.all().values_list('id', 'name')))
        COURSE_CHOICES = (COURSE_CHOICE_EMPTY + list(Course.objects.all().values_list('id', 'name')))
    except:
        CENTRE_CHOICES = ''
        COURSE_CHOICES = ''
    # CLASSES_CHOICES = (COURSE_CLASSES_EMPTY + list(Classes.objects.filter(start_date__gt=date.today()).values_list('id', 'name')))

    full_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"type": "text", "placeholder": _('Họ và tên (*)'), "class": "form-control"})
    )
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={"placeholder": _('Địa chỉ email (*)'), "class": "form-control"}))

    phone = forms.CharField(max_length=11, validators=[RegexValidator(regex="^\+?(?:0|84)(?:\d){9}$")],
                            widget=forms.TextInput(attrs={"type": "tel", "placeholder": _('Số điện thoại (*)'),
                                                          "pattern": "^\+?(?:0|84)(?:\d){9}$",
                                                          "class": "form-control"}))

    address = forms.CharField(max_length=255, required=False,
                              widget=forms.TextInput(
                                  attrs={"type": "text", "placeholder": _('Địa chỉ'), "class": "form-control"}))

    centre = forms.CharField(label="Trung tâm",
                             widget=forms.Select(choices=CENTRE_CHOICES,
                                                 attrs={"class": "form-control"}))
    course = forms.CharField(label="Khóa học",
                             widget=forms.Select(choices=COURSE_CHOICES, attrs={"class": "form-control"}))

    classes = forms.CharField(label="Lớp học",
                              widget=forms.Select(choices=COURSE_CLASSES_EMPTY, attrs={"class": "form-control"}))

    study_schedule_select = forms.CharField(
        widget=forms.Select(choices=STUDY_SHIFT_CHOICES,
                            attrs={"placeholder": _('Ca học'), "class": "form-control"}))
    title = forms.CharField(max_length=255,
                            widget=forms.TextInput(
                                attrs={"type": "text", "placeholder": _('Tiêu đề (*)'), "class": "form-control"}))
    transaction_id = forms.CharField(max_length=255, required=False,
                            widget=forms.TextInput(
                                attrs={"type": "text", "placeholder": _('Mã giao dịch'), "class": "form-control"}))
    payment_method = forms.CharField(required=False,
                                     widget=forms.Select(choices=[('', '---Chọn tài khoản nộp---'), (0, 'Tiền mặt'), (1, 'Tech'), (2, 'MB'), (3, 'BIDV')],
                                                         attrs={"placeholder": _('Tài khoản nộp'),
                                                                "class": "form-control"}))

    reward_code = forms.CharField(max_length=255, required=False,
                                  widget=forms.TextInput(
                                      attrs={"type": "text", "placeholder": _('Mã ưu đãi'), "class": "form-control"}))

    amount = forms.IntegerField(widget=forms.TextInput(
        attrs={"type": "number", "placeholder": _('Số tiền nộp (*)'), "class": "form-control"}))
    free_day_in_week = forms.CharField(max_length=255, required=False,
                                       help_text='Nhập các ngày bạn rảnh rỗi để chúng tôi có thể xếp lịch phù hợp cho bạn.',
                                       widget=forms.TextInput(attrs={"type": "text", "placeholder": _('Lịch rảnh'),
                                                                     "class": "form-control"}))

    def clean(self):
        super().clean()
        if self.is_valid():
            email = self.cleaned_data["email"]
            phone = self.cleaned_data["phone"]
            reward_code = self.cleaned_data["reward_code"]
            exist_email = AuthUser.objects.filter(email=email).count() > 0
            if exist_email:
                raise forms.ValidationError(_("Địa chỉ email đã được đăng ký vào hệ thống."))
            exist_phone = AuthUser.objects.filter(phone=phone).count() > 0
            if exist_phone:
                raise forms.ValidationError(_("Số điện thoại đã được đăng ký vào hệ thống."))
            exists_email_wait_review = StudentSendPaymentRequest.objects.filter(email=email, state=None).count() > 0
            if exists_email_wait_review:
                raise forms.ValidationError(
                    _("Địa chỉ email này đã được sử dụng để đăng ký tài khoản và đang chờ xét duyệt."))
            exists_phone_wait_review = StudentSendPaymentRequest.objects.filter(phone=phone, state=None).count() > 0
            if exists_phone_wait_review:
                raise forms.ValidationError(
                    _("Số điện thoại này đã được sử dụng để đăng ký tài khoản và đang chờ xét duyệt."))

            # Kiểm tra hợp lệ ưu đãi nếu có nhập ưu đãi
            check_valid_reward(reward_code, int(self.cleaned_data["course"]))


def check_valid_reward(reward_code, register_course_id):
    # Kiểm tra hợp lệ ưu đãi nếu có nhập ưu đãi
    if reward_code:
        exist_reward = Reward.objects.filter(code=reward_code).count() > 0
        if not exist_reward:
            raise forms.ValidationError(_("Mã ưu đãi không tồn tại."))
        reward = Reward.objects.get(code=reward_code)

        # Kiểm tra xem ưu đãi có hiệu lực hay không
        if not (reward.start_date <= date.today() <= reward.end_date):
            raise forms.ValidationError("Ưu đãi chỉ có hiệu lực từ ngày %s đến ngày %s."
                                        % (reward.start_date.strftime(DEFAULT_DATE_FORMAT),
                                           reward.end_date.strftime(DEFAULT_DATE_FORMAT)))

        # Kiểm tra ưu đãi có áp dụng cho khoá học này không.
        reward_courses = reward.course.values_list("id", flat=True)
        if reward_courses:
            apply_course = False
            for rc in reward_courses:
                if rc == register_course_id:
                    apply_course = True
            if not apply_course:
                raise forms.ValidationError(_("Mã ưu đãi không áp dụng cho khóa học này."))
        # Kiem tra xem het so luong chua
        reward_used_times = StudentDebt.objects.filter(reward=reward).count()
        if reward_used_times >= reward.quantity:
            raise forms.ValidationError(_("Mã ưu đãi đã hết số lượt sử dụng."))


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
        widget=forms.TextInput(attrs={
            "type": "email",
            "size": "30",
            "placeholder": _("E-mail address"),
        })
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        # self.users = filter_users_by_email(email)
        if not self.users:
            raise forms.ValidationError(_("The e-mail address is not assigned"
                                          " to any user account"))
        return self.cleaned_data["email"]
