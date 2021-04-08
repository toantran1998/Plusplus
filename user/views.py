from datetime import date, datetime

from django.db.models import Count, F, Sum, Case, When, IntegerField
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse
from django.shortcuts import render

from centre.models import Centre, ClassRoom, ClassesStudents, StudyShiftStudent, StudyShift
from manager.constant import GROUP, CENTRE_COLORS
from manager.utils import get_list_year_month
from user.models import AuthUser


def get_study_shift_chart_data_api(request):
    if request.method == 'GET':
        from_date = date(date.today().year, 1, 1)
        to_date = date(date.today().year, 12, 31)
        if 'from_date' in request.GET:
            from_date = datetime.strptime(request.GET['from_date'], '%Y-%m-%d')
        if 'to_date' in request.GET:
            to_date = datetime.strptime(request.GET['to_date'], '%Y-%m-%d')

        labels, datasets = get_centre_study_shift_data(from_date, to_date)
        return JsonResponse({'labels': labels, 'datasets': datasets})


def get_centre_study_shift_data(from_date, to_date):
    # Lay toi da 3 trung tam.
    centres = Centre.objects.all().order_by('id')[:4].values('id', 'name')
    number_days = (to_date - from_date).days
    number_weeks = int(number_days / 7)

    actual_study_shift = StudyShift.objects.filter(session_date__gte=from_date, session_date__lte=to_date)\
        .annotate(centre_id=F('classes__centre_id')).values('centre_id').annotate(count=Count('id'))
    count_max_study_shift = number_weeks * 6 * 4

    datasets = []
    data_actual_ss = []
    data_max_ss = []
    for centre in centres:
        data_max_ss.append(count_max_study_shift)
        max_s = 0
        for ass in actual_study_shift:
            if ass['centre_id'] == centre['id']:
                max_s = ass['count']
        data_actual_ss.append(max_s)

    datasets.append({'label': 'Số buổi học thực tế', 'backgroundColor': "#6495ED", 'data': data_actual_ss})
    datasets.append({'label': 'Số buổi học tối đa', 'backgroundColor': "#9FE2BF", 'data': data_max_ss})

    labels = list(centres.values_list('name', flat=True))
    return labels, datasets


def get_students_chart_data_api(request):
    if request.method == 'GET':
        from_date = date(date.today().year, 1, 1)
        to_date = date(date.today().year, 12, 31)
        if 'from_date' in request.GET:
            from_date = datetime.strptime(request.GET['from_date'], '%Y-%m-%d')
        if 'to_date' in request.GET:
            to_date = datetime.strptime(request.GET['to_date'], '%Y-%m-%d')

        labels, datasets = get_centre_students_data(from_date, to_date)
        return JsonResponse({'labels': labels, 'datasets': datasets})


def get_centre_students_data(from_date, to_date):
    # Lay toi da 3 trung tam.
    centres = Centre.objects.all().order_by('id')[:4].values('id', 'name')
    number_days = (to_date - from_date).days
    number_weeks = int(number_days / 7)

    sum_seats = ClassRoom.objects.all().values('centre_id')\
        .annotate(sum_seats=Sum('size')).values('centre_id', 'sum_seats')
    for i in range(len(sum_seats)):
        sum_seats[i]['max_students'] = sum_seats[i]['sum_seats'] * 4 * 6 * number_weeks

    number_cls_students = ClassesStudents.objects.filter(
        created_date_time__gte=from_date, created_date_time__lte=to_date) \
        .annotate(centre_id=F('classes__centre__id'))\
        .values('centre_id').annotate(
        count_waiting_students=Count(Case(
            When(state=1, then=1),
            output_field=IntegerField(),
        ))).annotate(
        count_cls_student=Count(Case(
            When(state=2, then=1),
            output_field=IntegerField(),
        ))).values('centre_id', 'count_waiting_students', 'count_cls_student')

    # attendance_info = StudyShiftStudent.objects.all() \
    #     .annotate(centre_id=F('student__user__centre__id'))\
    #     .values('centre_id').annotate(
    #     count_attendance=Count(Case(
    #         When(attendance=True, then=1),
    #         output_field=IntegerField(),
    #     ))).values('centre_id', 'count_attendance')

    datasets = []
    data_waiting_s = []
    data_cls_s = []
    data_attendance_s = []
    data_max_s = []

    for centre in centres:
        waiting_s = 0
        cls_s = 0
        attendance_s = 0
        max_s = 0

        for sum_s in sum_seats:
            if sum_s['centre_id'] == centre['id']:
                max_s = sum_s['max_students']
        data_max_s.append(max_s)

        for ncs in number_cls_students:
            if ncs['centre_id'] == centre['id']:
                waiting_s = ncs['count_waiting_students']
                cls_s = ncs['count_cls_student']
        data_waiting_s.append(waiting_s)
        data_cls_s.append(cls_s)

        # for ai in attendance_info:
        #     if ai['centre_id'] == centre['id']:
        #         attendance_s = ai['count_attendance']
        data_attendance_s.append(attendance_s)
    datasets.append({'label': 'Số SV chờ lớp', 'backgroundColor': "#6495ED", 'data': data_waiting_s})
    datasets.append({'label': 'Số SV được xếp lớp', 'backgroundColor': "#9FE2BF", 'data': data_cls_s})
    # datasets.append({'label': 'Số SV đi học', 'backgroundColor': "#40E0D0", 'data': data_attendance_s})
    # datasets.append({'label': 'Tổng số SV tối đa', 'backgroundColor': "#CCCCFF", 'data': data_max_s})

    labels = list(centres.values_list('name', flat=True))
    return labels, datasets


def get_users_chart_data_api(request):
    if request.method == 'GET':
        from_date = date(date.today().year, 1, 1)
        to_date = date(date.today().year, 12, 31)
        if 'from_date' in request.GET:
            from_date = datetime.strptime(request.GET['from_date'], '%Y-%m-%d')
        if 'to_date' in request.GET:
            to_date = datetime.strptime(request.GET['to_date'], '%Y-%m-%d')

        labels, datasets = get_monthly_users_data(from_date, to_date)
        return JsonResponse({'labels': labels, 'datasets': datasets})


def get_monthly_users_data(from_date, to_date):
    USER_GROUPS = [GROUP.RECEPTIONIST,
                   GROUP.STUDENT_CARE,
                   GROUP.TEACHER,
                   GROUP.STUDENT,
                   GROUP.BUSINESS]
    USER_LABELS = ['Lễ tân', 'CSHV', 'Giáo viên', 'Sinh viên', 'NVKD']
    qs = AuthUser.objects.all().filter(groups_id__in=USER_GROUPS)
    qs = qs.annotate(year=ExtractYear('created_date_time'), month=ExtractMonth('created_date_time'))
    qs = qs.values('groups_id', 'year', 'month').annotate(count=Count('id'))

    date_list = get_list_year_month(from_date, to_date)
    labels = list(date_list)
    datasets = []
    for i in range(len(USER_GROUPS)):
        # group = USER_GROUPS[i]
        data = []
        for label in labels:
            key = str(USER_GROUPS[i]) + '_' + label
            sum_amount = 0
            for q in qs:
                q_key = str(q['groups_id']) + "_" + str(q['year']) + str(q['month']).zfill(2)
                if key == q_key:
                    sum_amount = q['count']
            data.append(sum_amount)
        datasets.append({'label': USER_LABELS[i], 'backgroundColor': CENTRE_COLORS[i], 'data': data})
    return labels, datasets
