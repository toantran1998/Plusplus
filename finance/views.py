import math
from datetime import date, datetime, timedelta

from django.contrib.auth import hashers
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import format_html
from fcm_django.models import FCMDevice

from app_config.settings import DEFAULT_DATE_FORMAT
from centre.admin import add_student_to_study_shift
from centre.models import Centre, Course, Classes, ClassesStudents, StudyShift
from finance.forms import SearchDateRangeForm
from finance.models import StudentDebt, Payment, StudentSendPaymentRequest, Reward
from manager.constant import CENTRE_COLORS, GROUP
from manager.utils import date_format, currency, get_list_year_month, get_random_string, create_contract_info, \
    create_receipt_info
from message.views import send_email_create_user_success, send_email_to_user, send_notifications, \
    send_inform_approve_payment, send_inform_confirm_payment, send_inform_cancel_payment
from user.models import AuthUser, Student


@login_required
def view_dashboard_chart(request):
    # Handle request
    if request.method == 'GET':
        form = SearchDateRangeForm(request.GET)
        chart_type = None
        if 'chart_type' in request.GET:
            chart_type = request.GET['chart_type']
        if form.is_valid():
            return render(request, "admin/base_chart.html", {'form': form, 'chart_type': chart_type})
        return render(request, "admin/base_chart.html", {'form': SearchDateRangeForm(), 'chart_type': chart_type})


@login_required
def change_payment_request_state(request):
    if request.method == 'GET':
        if request.user.is_superuser or request.user.groups.id == GROUP.RECEPTIONIST:
            req_pay_id = int(request.GET['req_pay_id'])
            state = int(request.GET['state'])
            req_pay = StudentSendPaymentRequest.objects.get(id=req_pay_id)
            if not req_pay.state:
                req_pay.state = state
                req_pay.save()
                # Truong hop approve sinh vien.
                if state == 1:
                    create_or_update_student_info(request=request, req_pay=req_pay)
                elif state == 2:
                    # Gui email thong bao xac nhan lai thong tin thanh toan
                    send_inform_confirm_payment(req_pay)
                elif state == 3:
                    # Gui email thong bao huy thong tin thanh toan
                    send_inform_cancel_payment(req_pay)
                return JsonResponse({"result": "success"})
    return JsonResponse({"result": "Có lỗi xảy ra trong quá trình xử lý"})


def create_or_update_student_info(request, req_pay, default_password=None, add_to_classes=True, send_mail=True):
    # Truong hop sinh vien chua co tai khoan => Tao tk cho sinh vien
    exist_user = AuthUser.objects.filter(email=req_pay.email).count() > 0
    if not exist_user:
        random_password = get_random_string(8)
        user = AuthUser.objects.create(
            username=req_pay.email,
            full_name=req_pay.full_name,
            phone=req_pay.phone,
            email=req_pay.email,
            password=hashers.make_password(password=random_password),
            address=req_pay.address,
            date_joined=req_pay.send_date,
            centre=req_pay.centre, groups_id=GROUP.STUDENT)

        student = Student.objects.create(
            free_to_learn=req_pay.free_day_in_week,
            user=user,
            created_user=request.user, updated_user=request.user
        )
        user.user_code = "SV_" + str(student.id)
        if default_password:
            user.password = hashers.make_password(password=default_password)
        user.save()

        if send_mail:
            send_email_create_user_success(to_user=user,
                                           password=random_password,
                                           login_url=request.META['HTTP_HOST'] + ':' + '/admin/login')

    student = Student.objects.get(user__email=req_pay.email)
    exists_student_debt = StudentDebt.objects.filter(student=student, course=req_pay.course).count()
    if not exists_student_debt:
        # Nếu sv chưa có công nợ => tạo công nợ, hợp đồng cho sv và add sv vào lớp chờ của khoá đã đăng ký.
        plan_date = req_pay.plan_complete_date
        if not plan_date:
            plan_date = req_pay.send_date + timedelta(days=30)
        course = req_pay.course
        cost = course.cost
        study_shift_select = req_pay.study_schedule_select
        reward = req_pay.reward
        discount_percent = 0

        # Nếu sử dụng ưu đãi => tính giảm giá dựa trên giá gốc
        if reward:
            discount_percent = reward.discount_percent
            cost = (1 - discount_percent / 100) * course.cost
        else:
            # Nếu ko sử dụng ưu đãi => tính giá theo giá ca ngày hoặc tối
            if study_shift_select == 1 or study_shift_select == 2:
                cost = (1 - discount_percent / 100) * course.daytime_cost
            elif study_shift_select == 3 or study_shift_select == 4:
                cost = (1 - discount_percent / 100) * course.night_cost

        # Cho truong hop import tu file csv, thong tin so tien phai nop lay tu file csv.
        if req_pay.must_pay_amount > 0:
            cost = req_pay.must_pay_amount

        student_debt = StudentDebt.objects.create(
            centre=req_pay.centre, title=req_pay.title,
            student=student, course=req_pay.course,
            origin_amount=cost,
            rest_amount=cost,
            plan_date=plan_date,
            student_level=req_pay.student_level,
            reward=req_pay.reward,
            study_schedule_select=req_pay.study_schedule_select)

        apply_student_debt(student_debt=student_debt, course=req_pay.course,
                           owner=request.user, classes=req_pay.classes, add_to_classes=add_to_classes)

    # Tạo thông tin thanh toán
    student_debt = StudentDebt.objects.get(student=student, course=req_pay.course)
    payment = Payment.objects.create(student_debt=student_debt,
                                     paid_amount=req_pay.paid_amount,
                                     payment_method=req_pay.payment_method,
                                     completed_pay_date=req_pay.send_date)
    student_debt.rest_amount = student_debt.rest_amount - req_pay.paid_amount
    student_debt.save()

    # Link yêu cầu thanh toán tới công nợ tương ứng
    req_pay.student_debt = student_debt
    req_pay.save()
    if send_mail:
        send_inform_approve_payment(req_pay)


# def get_reward_by_code(request):
#     if request.method == 'GET':
#         if 'reward_code' in request.GET:
#             reward_code = request.GET['reward_code']
#             if Reward.objects.filter(code=reward_code).count() > 0:
#                 return JsonResponse({'reward': Reward.objects.get(code=reward_code)})
#
#         return JsonResponse({'reward': None})


def get_revenue_data_api(request):
    if request.method == 'GET':
        from_date = date(date.today().year, 1, 1)
        to_date = date(date.today().year, 12, 31)
        if 'from_date' in request.GET:
            from_date = datetime.strptime(request.GET['from_date'], '%Y-%m-%d')
        if 'to_date' in request.GET:
            to_date = datetime.strptime(request.GET['to_date'], '%Y-%m-%d')

        labels, datasets = get_monthly_revenue_data(from_date, to_date)
        return JsonResponse({'labels': labels, 'datasets': datasets})


def get_monthly_revenue_data(from_date, to_date):
    qs = Payment.objects.all().filter(
        completed_pay_date__gte=from_date, completed_pay_date__lte=to_date)
    qs = qs.annotate(centre_id=F('student_debt__student__user__centre__id'),
                     centre_name=F('student_debt__student__user__centre__name'),
                     year=ExtractYear('completed_pay_date'),
                     month=ExtractMonth('completed_pay_date'))
    qs = qs.values('centre_id', 'year', 'month')
    # qs = qs.annotate(key=Concat('centre_id', Value('_'), 'year', F('month').zfill(2)))
    qs = qs.annotate(sum_paid_amount=Sum(F('paid_amount')))
    qs = qs.values_list('centre_id', 'year', 'month', 'sum_paid_amount')

    # Lay toi da 5 trung tam.
    centres = Centre.objects.all().order_by('id')[:3].values('id', 'name')
    dates = get_list_year_month(from_date, to_date)
    labels = list(list(dates))
    datasets = []
    for i in range(len(centres)):
        centre = centres[i]
        data = []
        for label in labels:
            key = str(centre['id']) + '_' + label
            sum_amount = 0
            for q in qs:
                q_key = str(q[0]) + "_" + str(q[1]) + str(q[2]).zfill(2)
                if key == q_key:
                    sum_amount = q[3]
            data.append(sum_amount)
        datasets.append({'label': centre['name'], 'backgroundColor': CENTRE_COLORS[i], 'data': data})
    return labels, datasets


@login_required
def view_student_receipt(request):
    # Handle request
    if request.method == 'GET':
        if 'student_debt_id' in request.GET:
            student_debt_id = request.GET['student_debt_id']
            if student_debt_id:
                student_debts = StudentDebt.objects.filter(id=student_debt_id)
                if student_debts.count() > 0:
                    student_debt = student_debts[0]
                    contract = create_receipt_info(student_debt)
                    return render(request, "admin/student_receipt.html", context={'data': contract})
        elif 'req_pay_id' in request.GET:
            req_pay_id = request.GET['req_pay_id']
            req_pays = StudentSendPaymentRequest.objects.filter(id=req_pay_id)
            if req_pays.count() > 0:
                req_pay = req_pays[0]
                student_debt = req_pay.student_debt
                if not student_debt:
                    student_debts = StudentDebt.objects.filter(
                        centre=req_pay.centre, course=req_pay.course,
                        student__user__email=req_pay.email)
                    if student_debts.count() > 0:
                        student_debt = student_debts[0]
                if student_debt:
                    contract = create_receipt_info(student_debt)
                    contract.paid_amount = req_pay.paid_amount
                    return render(request, "admin/student_receipt.html", context={'data': contract})
    return render(request, "admin/404.html")


@login_required
def view_student_contract(request):
    # Handle request
    if request.method == 'GET':
        student_debt_id = None
        if 'student_debt_id' in request.GET:
            student_debt_id = request.GET['student_debt_id']
        if student_debt_id:
            student_debts = StudentDebt.objects.filter(id=student_debt_id)
            if student_debts.count() > 0:
                contract = create_contract_info(student_debts[0])

                return render(request, "admin/contract/index.html", context={'data': contract})
    return render(request, "admin/404.html")


def apply_student_debt(student_debt, course, owner, classes=None, add_to_classes=True):
    student_debt.contract = format_html("<a class='btn btn-primary' target='_blank' href='{url}'>{url_display}</a>",
                                        url='/admin/student/contract?student_debt_id=' + str(student_debt.pk), url_display='Xem')
    student_debt.receipt = format_html("<a class='btn btn-success' target='_blank' href='{url}'>{url_display}</a>",
                                       url='/admin/student/receipt?student_debt_id=' + str(student_debt.pk), url_display='Xem')

    if add_to_classes:
        # Add sv vào lớp chờ của khóa tương ứng. Nếu là khóa combo => add vào lớp chờ của khóa đầu tiên
        course_code = course.code
        course_code_array = course_code.split('_')

        # Truong hop khoa don le
        course_id = course.id

        next_next_course_code = None
        # Trường hợp là khóa combo
        if len(course_code_array) > 1:
            course_id = Course.objects.get(code=course_code_array[0]).id
            # Get khóa tiếp theo nữa của sv này
            next_next_course_code = course_code_array[1]

        # Trường hợp ko nhập thông tin classes => add sv vào lớp chờ mặc định là 2-5.
        # Ngược lại => add sinh viên vào lớp mà sv đã đăng ký.
        if not classes:
            classes = Classes.objects.get(course=course_id, day_in_week=1, centre=student_debt.student.user.centre, waiting_flag=True)
        class_student = ClassesStudents(classes=classes,
                                        student=student_debt.student, student_debt=student_debt,
                                        next_course_code=next_next_course_code,
                                        updated_user=owner, created_user=owner)
        if not classes.waiting_flag:
            # Nếu add sv vào lớp thường (ko phải lớp chờ)
            # => Đổi trạng thái thành đã nhận lớp
            class_student.state = 2
            # Thêm sv vào các buổi học của lớp đó
            study_shifts = StudyShift.objects.filter(classes=classes)
            add_student_to_study_shift(class_student, study_shifts)
        # add student into class of course
        class_student.save()
    student_debt.save()
