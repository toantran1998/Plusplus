import calendar
import datetime
import math
import random
import string
from collections import OrderedDict
from datetime import datetime, timedelta
from threading import Thread

from django.contrib import admin
from django.db.models import Sum
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils.html import format_html
from weasyprint import HTML, CSS

from app_config import settings
from centre.models import Course
from finance.models import Reward, Payment
from manager.constant import COURSES_INFO


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def currency(num):
    if not num:
        return 0
    return '{:,}'.format(num).replace(',', '.')


def start_new_thread(func):
    def decorator(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


# date input example: 19/11/2021
def dd_mm_yyyy_to_date(ddmmyyyy):
    arr_ddmmyyyy = ddmmyyyy.split('/')
    if len(arr_ddmmyyyy) == 3:
        return datetime(int(arr_ddmmyyyy[2]), int(arr_ddmmyyyy[1]), int(arr_ddmmyyyy[0]))
    return None

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def date_format(date_input, pattern=None):
    if date_input:
        if pattern:
            return date_input.strftime(pattern)
        return date_input.strftime(settings.DEFAULT_DATE_FORMAT)
    return None


def get_parent_object_from_request(self, request):
    """
    Returns the parent object from the request or None.

    Note that this only works for Inlines, because the `parent_model`
    is not available in the regular admin.ModelAdmin as an attribute.
    """
    resolved = resolve(request.path_info)
    if resolved.kwargs:
        return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
    return None


def create_user_label(name, code):
    return name + " (" + code + ")"


def str_to_int(str):
    if not str:
        return None
    else:
        return int(str)


def get_list_year_month(start_date, end_date):
    dates = [start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")]
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    return OrderedDict(((start + timedelta(_)).strftime(r"%Y%m"), None) for _ in range((end - start).days)).keys()


# method for import data from csv
def currency_to_int(curr):
    if not curr or curr == "-":
        return 0
    # Exam curr: 123.345.222
    return int(''.join(curr.split(".")))


def calculate_must_pay_amount(course_id, shift_select, reward_code=None):
    course = None
    reward = None
    if course_id:
        course = Course.objects.filter(id=course_id)

    if reward_code:
        reward = Reward.objects.filter(code=reward_code)

    must_pay_amount = 0
    if course and course.count() > 0:
        # Nếu có sử dụng ưu đãi thì tính giảm giá theo giá gốc
        if reward and reward.count() > 0:
            discount_percent = reward[0].discount_percent
            must_pay_amount = (1 - discount_percent / 100) * course[0].cost
        else:
            # Nếu ko sử dụng ưu đãi => tính giá theo giá ca ngày hoặc tối
            if shift_select == 1 or shift_select == 2:
                must_pay_amount = course[0].daytime_cost
            elif shift_select == 3 or shift_select == 4:
                must_pay_amount = course[0].night_cost

    return must_pay_amount


def create_contract_info(student_debt):
    student_user = student_debt.student.user
    student_debt.student.full_name = student_user.full_name
    student_debt.student.birth_day = date_format(student_user.birth_day)
    student_debt.student.email = student_user.email
    student_debt.student.phone = student_user.phone
    student_debt.plan_date = date_format(student_debt.plan_date)
    student_debt.must_pay_amount = currency(math.ceil(
        (1 - student_debt.discount_percent / 100) * student_debt.origin_amount))
    student_debt.origin_amount = currency(student_debt.origin_amount)
    student_debt.course_code = student_debt.course.code

    course_arr = student_debt.course_code.split("_")
    course_info = ''
    for c in course_arr:
        course = COURSES_INFO[c]
        content = "<tr><td>" + course['name'] + "</td><td>" + course['des'] + "</td></tr>"
        course_info = course_info + content
    student_debt.course_info = format_html(course_info)
    return student_debt


def create_receipt_info(student_debt):
    student_debt.paid_amount = Payment.objects.filter(student_debt=student_debt).aggregate(Sum('paid_amount'))['paid_amount__sum']
    if not student_debt.paid_amount:
        student_debt.paid_amount = 0
    student_debt.rest_amount = math.ceil((1 - student_debt.discount_percent / 100) * student_debt.origin_amount - student_debt.paid_amount)
    student_debt.student.user.birth_day = date_format(student_debt.student.user.birth_day)
    student_debt.plan_date = date_format(student_debt.plan_date)
    student_debt.completed_pay_date = date_format(student_debt.completed_pay_date)
    return student_debt


def html_to_pdf(template, data=None, stylesheets=None):
    if data:
        html_string = render_to_string(template, {"data": data})
    else:
        html_string = render_to_string(template)
    html = HTML(string=html_string)
    if not stylesheets:
        stylesheets = [CSS('static/assets/css/bootstrap.min.css')]
    return html.write_pdf(stylesheets=stylesheets)
