# Create your views here.
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from fcm_django.models import FCMDevice
from weasyprint import HTML, CSS

from finance.models import StudentDebt, Payment
from manager.constant import GROUP
from manager.utils import start_new_thread, create_contract_info, create_receipt_info, currency, html_to_pdf
from message.models import Notification
from message.send_email import send
from user.models import AuthUser


def send_email_reset_password(to_user, new_password, login_url):
    subject = '[ODIN] Reset mật khẩu thành công'
    data = to_user
    data.login_url = login_url
    data.new_password = new_password
    content = render_to_string("admin/email/reset_password.html", {"data": data})
    send_email_to_user(to_name=to_user.full_name, to_email=to_user.email, subject=subject, content=content)


def send_email_create_user_success(to_user, password, login_url):
    data = to_user
    data.password = password
    data.login_url = login_url
    content = render_to_string('admin/email/register_success.html', {'data': data})
    send_email_to_user(to_name=to_user.full_name, to_email=to_user.email,
                       subject='[ODIN] Đăng ký tài khoản thành công', content=content)


# email thông báo tới sv là đã nhận được thông tin đăng ký.
def send_inform_new_request_register_received(req_pay):
    send_content = render_to_string("admin/email/student/received_request_register.html",
                                    {"data": req_pay})
    send_email_to_user(to_name=req_pay.full_name, to_email=req_pay.email,
                       subject="[ODIN] Gửi yêu cầu đăng ký tài khoản thành công", content=send_content)


# Gửi thông báo sinh viên là yêu cầu thanh toán được phê duyệt
def send_inform_approve_payment(req_pay):
    content = render_to_string("admin/email/student/payment_approve.html", {"data": req_pay})
    subject = "[ODIN] Phê duyệt thông tin thanh toán"

    attach_file = None
    # Attach receipt
    student_debts = StudentDebt.objects.filter(
        centre=req_pay.centre, course=req_pay.course,
        student__user__email=req_pay.email)
    if student_debts.count() > 0:
        receipt = create_receipt_info(student_debts[0])
        receipt.paid_amount = currency(req_pay.paid_amount)
        pdf = html_to_pdf(template='admin/student_receipt.html', data=receipt)
        attach_file = {"name": "Hoá đơn thanh toán.pdf",
                       "content": pdf, "mimetype": "application/pdf"}
    send_inform_change_payment_status(
        to_name=req_pay.full_name, to_email=req_pay.email, subject=subject, content=content, attach_files=[attach_file])
    # Nếu đã tạo công nợ và là lần đầu thanh toán => gửi hợp đồng công nợ cho sinh viên
    if attach_file and Payment.objects.filter(student_debt__id__in=student_debts.values_list("id", flat=True)).count() == 1:
        send_email_create_contract(req_pay=req_pay)


# Gửi hợp đồng cho sinh viên
def send_email_create_contract(req_pay):
    content = render_to_string("admin/email/student/create_contract.html", {"data": req_pay})
    subject = "[ODIN] Hợp đồng khoá học"

    student_debts = StudentDebt.objects.filter(
        centre=req_pay.centre, course=req_pay.course,
        student__user__email=req_pay.email)
    if student_debts.count() > 0:
        contract = create_contract_info(student_debts[0])
        pdf = html_to_pdf(template='admin/contract/index.html', data=contract,
                          stylesheets=[
                              CSS('static/css/contract.css'),
                              CSS('static/assets/css/bootstrap.min.css')])
        attach_file = {"name": "Hợp đồng khoá học sinh viên %s.pdf" % req_pay.full_name,
                       "content": pdf, "mimetype": "application/pdf"}
        send_email_to_user(
            to_name=req_pay.full_name, to_email=req_pay.email, subject=subject, content=content,
            attach_files=[attach_file])


# Gửi thông báo sinh viên là yêu cầu thanh toán cần xem lại
def send_inform_confirm_payment(req_pay):
    content = render_to_string("admin/email/student/payment_confirm.html", {"data": req_pay})
    subject = "[ODIN] Thông tin thanh toán không chính xác"
    send_inform_change_payment_status(to_name=req_pay.full_name, to_email=req_pay.email, subject=subject, content=content)


# Gửi thông báo sinh viên là yêu cầu thanh toán cần xem lại
def send_inform_cancel_payment(req_pay):
    content = render_to_string("admin/email/student/payment_reject.html", {"data": req_pay})
    subject = "[ODIN] Huỷ thông tin thanh toán"
    send_inform_change_payment_status(to_name=req_pay.full_name, to_email=req_pay.email, subject=subject, content=content)


def send_inform_change_payment_status(to_name, to_email, subject, content, attach_files=None):
    send_email_to_user(to_name=to_name, to_email=to_email,
                       subject=subject, content=content, attach_files=attach_files)
    to_user_ids = AuthUser.objects.filter(email=to_email).values_list("id", flat=True)
    if to_user_ids.count() > 0:
        send_notifications(devices=FCMDevice.objects.filter(
            user_id__in=to_user_ids),
            title=subject,
            content=content)


# Gửi thông báo tới lễ tân và admin khi có yêu cầu thanh toán mới
def send_inform_has_new_payment_request(req_pay):
    subject = "[ODIN] Yêu cầu thanh toán từ học viên %s" % req_pay.full_name
    receive_users = AuthUser.objects.filter(Q(is_superuser=True)
                                            | Q(groups_id=GROUP.RECEPTIONIST,
                                                centre_id=req_pay.centre_id))
    send_content = render_to_string("admin/email/employee/new_request_payment.html",
                                    {"data": req_pay})
    for user in receive_users:
        detail_content = send_content.replace("{employee_name}", user.full_name)
        send_email_to_user(to_name=user.full_name, to_email=user.email, subject=subject,
                           content=detail_content)
        send_notifications(devices=FCMDevice.objects.filter(
            user_id__in=receive_users.values_list("id", flat=True)),
            title=subject,
            content=detail_content)


# email thông báo có sv gửi yêu cầu đăng ký tk tới lễ tân và admin.
def send_inform_new_request_register(req_pay):
    # Gửi email và notify tới lễ tân của trung tâm và admin
    subject = "[ODIN] Yêu cầu đăng ký học viên mới %s" % req_pay.full_name
    send_content = render_to_string("admin/email/employee/new_request_register.html", {"data": req_pay})
    receive_users = AuthUser.objects.filter(Q(is_superuser=True)
                                            | Q(groups_id=GROUP.RECEPTIONIST, centre_id=req_pay.centre_id))
    for user in receive_users:
        detail_content = send_content.replace("{employee_name}", user.full_name)
        send_email_to_user(to_name=user.full_name, to_email=user.email, subject=subject, content=detail_content)
        send_notifications(devices=FCMDevice.objects.filter(
                user_id__in=receive_users.values_list("id", flat=True)),
                title=subject,
                content=detail_content)


# @start_new_thread
# def send_email_update_user(to_name, to_username, to_address):
#     data = {'to_name': to_name}
#     body = render_to_string('admin/email/student/register_success.html', {'data': data})
#     send(to=to_address, subject='[ODIN] Cập nhật thông tin cá nhân'
#          , body=body)


def send_inform_join_classes_to_teacher(to_user, cls):
    # Gửi thông báo tới những giáo viên được thêm vào lớp
    # data = cls
    # data.count_sty
    content = render_to_string('admin/email/teacher/join_classes_inform.html', {'data': cls})
    subject = "[ODIN] Kính mời thầy/cô tham gia lớp học %s" % cls.name
    send_email_to_user(to_name=to_user.full_name, to_email=to_user.email,
                       subject=subject, content=content)
    send_notifications(
        devices=FCMDevice.objects.filter(user_id=to_user.id), title=subject, content=content)


@start_new_thread
def send_email_to_user(to_name, to_email, subject, content, attach_files=None):
    send(to=to_email, subject=subject, body=content, attach_files=attach_files)


def send_bulk_emails(users, subject, content):
    for user in users:
        send_email_to_user(to_name=user.full_name, to_email=user.email, subject=subject, content=content)


@login_required
def send_token_api(request):
    if request.method == 'GET':
        registration_id = request.GET['registration_id']
        exists_user_token = FCMDevice.objects.filter(registration_id=registration_id, user=request.user).count() > 0
        if not exists_user_token:
            exists_token = FCMDevice.objects.filter(registration_id=registration_id)
            if exists_token.count() > 0:
                exists_token.delete()
            device = FCMDevice(registration_id=registration_id,
                               active=True, type='web', user=request.user)
            device.save()
        return JsonResponse({'success': True})


def count_unread_messages_api(request):
    count = Notification.objects.filter(to_user_id=request.user.id, viewed_state=False).count()
    return JsonResponse({'count': count})


@start_new_thread
def send_notifications(devices, title, content):
    devices.send_message(title=title, body=content)
    user_ids = devices.values_list("user_id", flat=True).distinct()
    for user_id in user_ids:
        notify = Notification(title=title, content=content,
                              to_user_id=user_id, sent_date=datetime.today())
        notify.save()


@login_required
def send_message_api(request):
    if request.method == 'GET':
        devices = FCMDevice.objects.all()
        send_notifications(devices=devices,
                           title="Thông báo tạo mới khóa học",
                           # from_user=request.user,
                           # data={"url": "demo", "icon": "demo"},
                           content="demo test")
        # devices.send_message(title="Title", body="Message")
        # devices.send_message(title="Title", body="Message", data={"test": "test"})
        # devices.send_message(data={"test": "test"})
        return JsonResponse({'success': True})


def read_message_api(request):
    if request.method == 'GET':
        notification_id = request.GET['notification_id']
        notification = Notification.objects.get(id=notification_id)
        notification.viewed_state=True
        notification.save()
        return JsonResponse({'success': True})
