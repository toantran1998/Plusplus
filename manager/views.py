# Create your views here.
import csv
import datetime
import json
from datetime import date

from django.contrib.auth import hashers
from django.contrib.auth.forms import PasswordResetForm
from django.core import serializers
from django.db.models import F
from django.db.models import Sum, Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from fcm_django.models import FCMDevice
from weasyprint import HTML, CSS

from app_config.settings import DEFAULT_DATE_FORMAT
from centre.models import Classes, ClassesStudents, StudyShift, Centre, Course
from finance.models import StudentDebt, Payment, StudentSendPaymentRequest, Reward
from finance.views import create_or_update_student_info
from manager import DT_Student_Data, TDN_Student_Data, TQV_Student_Data
from manager.constant import GROUP
from manager.form import RegistrationForm
from manager.utils import currency, get_random_string, dd_mm_yyyy_to_date, currency_to_int, calculate_must_pay_amount, \
    html_to_pdf
from message.views import send_email_reset_password, send_email_to_user, send_bulk_emails, send_notifications, \
    send_inform_new_request_register, send_inform_new_request_register_received
from user.models import AuthUser, Student, Teacher


def download_pdf(request):
    student_debt = StudentDebt.objects.get(id=2)
    response = HttpResponse(html_to_pdf(template='admin/student_receipt.html', data=student_debt),
                            content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=NameOfFile'
    return response


def student_register(response):
    if response.method == "POST":
        form = RegistrationForm(response.POST)
        form.is_success = False
        if form.is_valid():
            cld = form.cleaned_data
            # if 'apply_reward' in cld:
            #     reward_code = cld['reward_code']
            #     course_id = cld['course_id']
            #     check_valid_reward(reward_code, course_id)
            #     reward = Reward.objects.get(code=reward_code)
            #     if reward.type == 1:
            #         form.reward_info = "Ưu đãi giảm giá: %s%s" % (str(reward.discount_percent), '%')
            #     if reward.type == 2:
            #         form.reward_info = "Ưu đãi quà tặng: %s" % (str(reward.gift))
            # else:
            must_pay_amount = calculate_must_pay_amount(
                course_id=int(cld['course'].strip()), shift_select=int(cld['study_schedule_select']), reward_code=cld['reward_code'].strip())
            req_pay = StudentSendPaymentRequest.objects.create(
                title=cld['title'].strip(),
                transaction_id=cld['transaction_id'].strip(),
                free_day_in_week=cld['free_day_in_week'].strip(),
                centre_id=cld['centre'].strip(), full_name=cld['full_name'].strip(),
                email=cld['email'].strip(), phone=cld['phone'].strip(), address=cld['address'].strip(),
                course_id=int(cld['course'].strip()),
                payment_method=cld['payment_method'].strip(),
                must_pay_amount=must_pay_amount,
                study_schedule_select=int(cld['study_schedule_select']), paid_amount=cld['amount']
            )

            if cld['classes'].strip():
                req_pay.classes_id = int(cld['classes'].strip())
                clss = Classes.objects.filter(id=req_pay.classes_id)
                if clss.count() > 0:
                    cls = clss[0]
                    # Truong hop sinh vien chon 1 lop thuong (ko la lop cho) => set ca hoc la ca hoc cua lop do.
                    if not cls.waiting_flag:
                        req_pay.study_schedule_select = cls.study_shift_select


            if cld['reward_code'].strip() and Reward.objects.filter(code=cld['reward_code'].strip()).count() > 0:
                req_pay.reward = Reward.objects.get(code=cld['reward_code'].strip())

            req_pay.save()

            # Gui email thong bao tới sv da nhan duoc request dang ky va thong tin thanh toan
            send_inform_new_request_register_received(req_pay=req_pay)
            # Gửi email và notify tới lễ tân của trung tâm
            send_inform_new_request_register(req_pay)
            form.is_success = True
        return render(response, "admin/student_register.html", {"form": form})

    return render(response, "admin/student_register.html", {"form": RegistrationForm()})


# Lấy số tiền cần thanh toán cho mh đăng ký sinh viên.
def get_must_pay_amount_api(request):
    if request.method == 'GET':
        course_id = None
        shift_select = None
        reward_code = None
        if 'course_id' in request.GET and request.GET['course_id']:
            course_id = request.GET['course_id']

        if 'reward_code' in request.GET and request.GET['reward_code']:
            reward_code = request.GET['reward_code'].strip()

        if 'shift_select' in request.GET and request.GET['shift_select']:
            shift_select = int(request.GET['shift_select'].strip())

        must_pay_amount = calculate_must_pay_amount(course_id=course_id, shift_select=shift_select, reward_code=reward_code)

        return JsonResponse({'result': "success", 'must_pay_amount': currency(must_pay_amount)})


# Lấy ds class chưa bắt đầu làm listbox cho mh đăng ký tài khoản sv.
def get_classes_by_centre_and_course(request):
    if request.method == 'GET':
        centre = None
        if 'centre' in request.GET and request.GET['centre']:
            centre = request.GET['centre']
        course = None
        if 'course' in request.GET and request.GET['course']:
            course = Course.objects.filter(id=request.GET['course'])
        classes = Classes.objects.filter(Q(start_date__gt=date.today()) | Q(waiting_flag=True))
        if centre:
            classes = classes.filter(centre=centre)
        if course:
            # Nếu khoá đăng ký là khoá commbo => chỉ lấy ra ds lớp học của khoá đầu tiên trong khoá commbo.
            first_course_code = course[0].code.split("_")[0]
            classes = classes.filter(course__code=first_course_code)

        # classes = classes.values("id", "name")
        classes_json = serializers.serialize('json', classes)
        return JsonResponse({'result': "success", 'classes': classes_json})


def get_reward_by_code(request):
    if request.method == 'GET':
        try:
            reward_code = request.GET['reward_code']
            if not reward_code:
                return JsonResponse({'result': "error", 'message': 'Vui lòng nhập mã ưu đãi bạn muốn áp dụng.'})
            exist_reward = Reward.objects.filter(code=reward_code).count() > 0
            if not exist_reward:
                return JsonResponse({'result': "error", 'message': 'Mã ưu đãi không tồn tại.'})
            reward_json = serializers.serialize('json', Reward.objects.filter(code=reward_code))
            return JsonResponse({'result': "success", 'reward': reward_json})
        except Exception as e:
            return JsonResponse({'result': "error", 'message': str(e)})


# API get thông tin lịch học trên màn hình lịch học theo tuần.
def get_study_shifts_by_date_range_api(request):
    if request.method == 'GET':
        try:
            from_date = date.today() - datetime.timedelta(days=date.today().weekday())
            to_date = from_date + datetime.timedelta(days=6)
            classes_id = None
            centre_id = None
            # Trường hợp là super admin
            if request.user.is_superuser:
                if 'centre' in request.GET and request.GET['centre']:
                    centre_id = int(request.GET['centre'])
            else:
                centre_id = request.user.centre.id
            if 'from_date' in request.GET and request.GET['from_date']:
                from_date = datetime.datetime.strptime(request.GET['from_date'], '%Y-%m-%d')
            if 'to_date' in request.GET and request.GET['to_date']:
                to_date = datetime.datetime.strptime(request.GET['to_date'], '%Y-%m-%d')
            if 'classes' in request.GET and request.GET['classes']:
                classes_id = int(request.GET['classes'])
            study_shifts = StudyShift.objects.filter(
                session_date__gte=from_date,
                session_date__lte=to_date)
            if centre_id:
                study_shifts = study_shifts.filter(classes__centre__id=centre_id)
            if classes_id:
                study_shifts = study_shifts.filter(classes_id=classes_id)
            study_shifts = study_shifts.annotate(classes_name=F('classes__name'))\
                .values('classes_name', 'class_room', 'order_no', 'session_date', 'from_time', 'to_time', 'study_shift_select')

            # study_shifts_json = serializers.serialize('json', study_shifts)
            # return HttpResponse(json.dumps(list(study_shifts)))
            return JsonResponse({'result': "success", 'study_shifts': list(study_shifts)})
        except Exception as e:
            return JsonResponse({'result': "error", 'message': str(e)})


def get_dashboard_header_data(request):
    if request.method == 'GET':
        count_users = currency(AuthUser.objects.all().count())
        count_students = currency(Student.objects.all().count())
        count_teachers = currency(Teacher.objects.all().count())
        count_classes = currency(Classes.objects.all().count())
        count_contracts = currency(StudentDebt.objects.all().count())
        sum_revenues = Payment.objects.aggregate(Sum('paid_amount'))['paid_amount__sum']
        sum_remain_amount = StudentDebt.objects.aggregate(Sum('rest_amount'))['rest_amount__sum']

        # Tổng SV/Tổng SV hoàn phí/Tổng SV chờ lớp/Tổng SV đang học/Tổng SV tốt nghiệp
        # Tổng sv hoàn phí
        count_back_amount_students = currency(StudentDebt.objects.filter(back_amount__gt=0).count())
        # Tổng sv chờ lớp (tổng sv trong lớp chờ)
        count_waiting_cls_students = currency(ClassesStudents.objects.filter(state=1).count())
        # Tổng sv đang học
        number_students_students = currency(ClassesStudents.objects.filter(state=2).count())
        # Tổng sv tốt nghiệp
        number_graduated_students = currency(ClassesStudents.objects.filter(state=3).count())
        number_students_statics = "%s/%s/%s/%s%s" % (str(count_students), str(count_back_amount_students),
                                                     str(count_waiting_cls_students), str(number_students_students),
                                                     str(number_graduated_students))
        # Tổng lớp đã khai giảng
        number_started_classes = currency(Classes.objects.filter(start_date__lte=date.today()).count())

        # Tổng buổi học đã hoàn thành
        number_study_shift_complete = StudyShift.objects.filter(Q(session_date__lt=date.today())).count() \
                                      + StudyShift.objects.filter(Q(session_date=date.today()),
                                                                  Q(to_time__lt=datetime.datetime.now().time())).count()
        number_study_shift = StudyShift.objects.all().count()

        # Tổng buổi học đã hoàn thành/Tổng buổi học còn phải hoàn thành
        number_study_shift_statics = "%s/%s" % (str(currency(number_study_shift_complete)),
                                                str(currency(number_study_shift - number_study_shift_complete)))

        sum_discount = StudentDebt.objects.all().values('origin_amount', 'discount_percent').annotate(
            discount=F('origin_amount') * F('discount_percent') / 100).aggregate(Sum('discount'))['discount__sum']

        return JsonResponse({'number_users': count_users,
                             'number_students': count_students,
                             'number_teachers': count_teachers,
                             'number_classes': count_classes,
                             'number_contracts': count_contracts,
                             'number_revenues': currency(sum_revenues),
                             'sum_remain_amount': currency(sum_remain_amount),
                             'number_students_statics': number_students_statics,
                             'number_started_classes': number_started_classes,
                             'number_study_shift_statics': number_study_shift_statics,
                             'sum_discount': currency(sum_discount)})


@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if AuthUser.objects.filter(email=email).count() > 0:
                user = AuthUser.objects.get(email=email)
                random_password = get_random_string(8)
                user.password = hashers.make_password(password=random_password)
                user.save()

                send_email_reset_password(
                    to_user=user,
                    new_password=random_password,
                    login_url=request.META['HTTP_HOST'] + '/admin/login')
                form.is_success = True
            else:
                form.add_error('email', 'Địa chỉ email không tồn tại.')
        return render(request, "admin/password_reset.html", context={'form': form})
    else:
        return render(request, "admin/password_reset.html", context={'form': PasswordResetForm()})


# Chức năng để import student từ csv file
def import_students(request):
    if request.method == 'GET':
        data_list = []
        centre_id = int(request.GET['centre'])
        centre = Centre.objects.get(id=centre_id)
        if centre_id == 3:
            data_list = csv.reader(open('/opt/projects/mc_ecm/dongtac_full.csv'))
        if centre_id == 2:
            data_list = csv.reader(open('/opt/projects/mc_ecm/trandainghia_full.csv'))
        if centre_id == 1:
            data_list = csv.reader(open('/opt/projects/mc_ecm/tranquocvuong_full.csv'))
        failed_records = []
        idx = 0
        print("Start processing:")
        for row in data_list:
            idx = idx + 1
            print("Processing record:%s" % (str(idx)))
            if idx > 2:
                try:
                    arr = str(row).split(';')
                    date_joined = dd_mm_yyyy_to_date(arr[1].strip())
                    # birth_day = dd_mm_yyyy_to_date(arr[5].strip())

                    must_pay_amount = currency_to_int(arr[14].strip())
                    paid_amount = currency_to_int(arr[7].strip())

                    level_code = arr[18].strip()
                    if level_code == 'BB':
                        level_code = 1
                    elif level_code == 'C':
                        level_code = 2
                    elif level_code == 'IE1':
                        level_code = 3
                    elif level_code == 'IE2':
                        level_code = 4
                    elif level_code == 'IE3':
                        level_code = 5
                    elif level_code == 'TO1':
                        level_code = 6
                    elif level_code == 'TO2':
                        level_code = 7
                    else:
                        level_code = None

                    course_id = arr[12].strip()
                    if course_id.isnumeric() and Course.objects.filter(id=course_id).count() > 0:
                        course_id = int(arr[12].strip())
                    else:
                        if StudentDebt.objects.filter(student__user__email=arr[5].strip()).count() == 1:
                            course_id = StudentDebt.objects.get(student__user__email=arr[5].strip()).course.id
                        else:
                            course_id = 17  # default course
                    req_pay = StudentSendPaymentRequest(
                        title='Công nợ sinh viên %s' % arr[5].strip(),
                        must_pay_amount=must_pay_amount,
                        centre_id=centre_id, full_name=arr[2].strip(),
                        email=arr[5].strip(), phone=arr[4].strip(),
                        student_level=level_code,
                        send_date=date_joined,
                        course_id=int(course_id), study_schedule_select=1, paid_amount=paid_amount
                    )

                    create_or_update_student_info(
                        request=request, req_pay=req_pay, default_password='123456c@', add_to_classes=False, send_mail=False)

                    student_state = arr[19].strip()
                    student = Student.objects.filter(user__email=arr[5].strip())
                    if student.count() > 0:
                        student = Student.objects.get(user__email=arr[5].strip())
                        if student_state == "Tốt nghiệp":
                            student.state = 3
                        if student_state == "Bảo lưu":
                            student.state = 4
                        if student_state == "Xếp lớp":
                            student.state = 2
                        if student_state == "Nhận lớp":
                            student.state = 2
                        if student_state == "Rút quyền lợi":
                            student.state = 7
                        student.save()
                except Exception as e:
                    failed_records.append({'row': str(row), 'error': str(e)})
                pass
        print("Finish processing")
        return JsonResponse({'errors': failed_records})


def import_student_debts(request):
    if request.method == 'GET':
        centre_id = int(request.GET['centre'])
        centre = Centre.objects.get(id=centre_id)

        data_list = []
        if centre_id == 3:
            data_list = DT_Student_Data.DT_STUDENT_DATA
        if centre_id == 2:
            data_list = TDN_Student_Data.DT_STUDENT_DATA
        if centre_id == 1:
            data_list = TQV_Student_Data.DT_STUDENT_DATA

        failed_records = []
        for idx in range(len(data_list)):
            data = data_list[idx]
            try:
                arr = data.split(',')
                user = AuthUser(
                    username=arr[3].strip(),
                    full_name=arr[1].strip(),
                    phone=arr[2].strip(),
                    email=arr[3].strip(),
                    password=hashers.make_password(password='123456c@'),
                    centre=centre, groups_id=GROUP.STUDENT)
                if len(arr) == 5:
                    birth_day = arr[4].strip()
                    if birth_day:
                        birth_day = dd_mm_yyyy_to_date(birth_day)
                        user.birth_day = birth_day
                    date_joined = arr[0].strip()
                    if date_joined:
                        date_joined = dd_mm_yyyy_to_date(date_joined)
                        user.date_joined = date_joined
                    user.save()

                    student = Student.objects.create(
                        user=user,
                        created_user=request.user, updated_user=request.user
                    )
                    user.user_code = "SV_" + str(student.id)
                    user.save()
            except Exception as e:
                failed_records.append({'No': idx, 'message': str(e)})
                pass
        return JsonResponse({'errors': failed_records})

