from datetime import date, timedelta, datetime

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from centre.models import StudyShiftStudent, Classes
from finance.forms import SearchDateRangeForm, SearchStudyShiftForm
from finance.models import StudentDebt
from manager.constant import GROUP
from manager.form import COURSE_CLASSES_EMPTY
from user.models import Student


@login_required
def view_study_shift_schedule(request):
    # Handle request
    if request.method == 'GET':
        form = SearchStudyShiftForm(request.GET)
        if form.is_valid():
            return render(request, "admin/study_shift_content.html", {'form': form})

        form = SearchStudyShiftForm()
        return render(request, "admin/study_shift_content.html", {'form': form})


def get_default_study_shift_session_date(request):
    user = request.user

    if user.is_superuser or user.groups.id != GROUP.STUDENT_CARE:
        default_date = date.today()
    else:
        default_date = date.today() - timedelta(days=1)
    return JsonResponse({"default_session_date": default_date})


@login_required
# Get danh sách classes để làm đk search trên màn hình buổi học calendar.
def get_classes_api(request):
    if request.method == 'GET':
        classes = None
        if request.user.is_superuser:
            classes = Classes.objects.all()
        elif request.user.groups.id == GROUP.STUDENT_CARE or request.user.groups.id == GROUP.STUDENT_CARE:
            classes = Classes.objects.filter(centre=request.user.centre)
        classes = classes.filter(waiting_flag=False)
        classes_json = serializers.serialize('json', classes)
        return JsonResponse({"result": "success", "classes": classes_json})


def task_students_list(request):
    if request.method == "GET":
        student_type = request.GET["type"]
        results = None
        if student_type == 'STUDENT_LOST_CONFIRM':
            results = Student.objects.filter(state=5).annotate(
                full_name=F('user__full_name'), code=F('user__user_code'), phone=F('user__phone'), email=F('user__email')) \
                .values('full_name', 'code', 'phone', 'email')
        elif student_type == 'STUDENT_OFF_YESTERDAY':
            yesterday = date.today() - timedelta(days=1)
            results = StudyShiftStudent.objects.filter(study_shift__session_date=yesterday, attendance=False)\
                .annotate(full_name=F('student__user__full_name'), code=F('student__user__user_code'),
                          phone=F('student__user__phone'), email=F('student__user__email')) \
                .values('full_name', 'code', 'phone', 'email')
        elif student_type == 'STUDENT_OFF_OVER_TWO_DAYS':
            results = StudyShiftStudent.objects.filter(study_shift__session_date__lt=date.today(), attendance=False)\
                .values('student__id', 'student__user__full_name', 'student__user__user_code').annotate(off_times=Count('id'))
            results = results.filter(off_times__gte=2)\
                .annotate(full_name=F('student__user__full_name'), code=F('student__user__user_code'),
                          phone=F('student__user__phone'), email=F('student__user__email')) \
                .values('full_name', 'code', 'phone', 'email')
        elif student_type == 'STUDENT_PAYMENT_DEADLINE':
            next_seven_date = datetime.now() + timedelta(days=7)
            results = StudentDebt.objects.filter(plan_date__lte=next_seven_date, rest_amount__gt=0) \
                .annotate(full_name=F('student__user__full_name'), code=F('student__user__user_code'),
                          phone=F('student__user__phone'), email=F('student__user__email')) \
                .values('full_name', 'code', 'phone', 'email')

        return render(request, "admin/task_student_list.html", {"results": results})

