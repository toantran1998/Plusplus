from datetime import datetime, date, timedelta

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from centre.models import StudyShiftSchedule, Classes, Centre
from finance.models import StudentDebt
from manager.form import CENTRE_CHOICE_EMPTY


class SearchDateRangeForm(forms.Form):
    from_date = forms.DateField(
        required=True,
        widget=DatePickerInput(format='%d/%m/%Y'),
        initial=date(datetime.today().year, 1, 1)
    )

    to_date = forms.DateField(
        required=True,
        widget=DatePickerInput(format='%d/%m/%Y'),
        initial=datetime.today()
    )

    def clean(self):
        super().clean()
        from_date = None
        to_date = None
        if "from_date" in self.cleaned_data:
            from_date = self.cleaned_data['from_date']
        if "to_date" in self.cleaned_data:
            to_date = self.cleaned_data['to_date']
        if from_date and to_date and to_date < from_date:
            raise ValidationError("Nhập khoảng thời gian tìm kiếm không hợp lệ.")


class SearchStudyShiftForm(ModelForm):
    try:
        CENTRE_CHOICES = (CENTRE_CHOICE_EMPTY + list(Centre.objects.all().values_list('id', 'name')))
        CLASSES_CHOICES = (list(Classes.objects.all().values_list('id', 'name')))
    except:
        CENTRE_CHOICES = ''
        CLASSES_CHOICES = ''
    centre = forms.CharField(label="Trung tâm",
                             widget=forms.Select(choices=CENTRE_CHOICES,
                                                 attrs={}))
    from_date = forms.DateField(
        required=True,
        widget=forms.HiddenInput(),
        initial=(date.today() - timedelta(days=date.today().weekday()))
    )

    to_date = forms.DateField(
        required=True,
        widget=forms.HiddenInput(),
        initial=(date.today() - timedelta(days=date.today().weekday()) + timedelta(days=6))
    )

    classes = forms.CharField(label="Lớp học", required=False,
                              widget=forms.HiddenInput())
    def clean(self):
        super().clean()
        from_date = None
        to_date = None
        if "from_date" in self.cleaned_data:
            from_date = self.cleaned_data['from_date']
        if "to_date" in self.cleaned_data:
            to_date = self.cleaned_data['to_date']
        if from_date and to_date and to_date < from_date:
            raise ValidationError("Nhập khoảng thời gian tìm kiếm không hợp lệ.")

    class Meta:
        model = StudyShiftSchedule
        exclude = ("",)


class StudentDebtForm(ModelForm):
    def clean(self):
        if self.is_valid():
            cleaned_data = super().clean()
            if not self.instance.pk:
                register_courses = None
                if 'course' in cleaned_data:
                    course = cleaned_data['course']
                    if 'student' in cleaned_data:
                        student = cleaned_data['student']
                        # Kiem tra xem neu sinh vien da đăng ký công nợ khoá học này hay chưa
                        if StudentDebt.objects.filter(student=student, course=course).count() > 0:
                            raise ValidationError("Sinh viên đã được đăng ký vào khóa học %s rồi." % course.name)

    class Meta:
        model = StudentDebt
        exclude = ("",)
        # fields = ['pub_date', 'headline', 'content', 'reporter']
