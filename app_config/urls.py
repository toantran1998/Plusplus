"""app_config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from fcm_django.api.rest_framework import FCMDeviceViewSet
from rest_framework.routers import DefaultRouter

# from manager.views import export_receipt_pdf
from centre.views import task_students_list, get_default_study_shift_session_date, view_study_shift_schedule, \
    get_classes_api
from finance.views import view_student_receipt, view_student_contract, view_dashboard_chart, get_revenue_data_api, \
    change_payment_request_state
from manager.sites import CustomAdminSite
from manager.views import reset_password, get_dashboard_header_data, import_students, student_register, \
    get_reward_by_code, get_classes_by_centre_and_course, get_study_shifts_by_date_range_api, get_must_pay_amount_api, \
    html_to_pdf, download_pdf
from message.views import send_token_api, send_message_api, count_unread_messages_api, read_message_api
from user.views import get_users_chart_data_api, get_students_chart_data_api, get_study_shift_chart_data_api

router = DefaultRouter()
router.register(r'devices', FCMDeviceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url('admin/notification/', TemplateView.as_view(template_name='admin/firebase/index.html'), name='notification'),
    url('admin/phieuthu/', TemplateView.as_view(template_name='admin/student_receipt.html'), name='phieuthu'),
    url('admin/student/receipt/', view_student_receipt, name='view_student_receipt'),
    url('admin/student/contract/', view_student_contract, name='view_student_contract'),
    url('admin/view/chart/', view_dashboard_chart, name='view_chart'),
    url('admin/send-token/', send_token_api, name='send-token-api'),
    url('admin/send-message/', send_message_api, name='send-message-api'),
    url('admin/count-unread-message/', count_unread_messages_api, name='count-unread-message'),
    url('admin/read-message/', read_message_api, name='read_message_api'),
    url('admin/student/import/', import_students, name='import_students'),
    url('admin/task-student-list/', task_students_list, name='task_students_list'),
    url('admin/study-shift/default-session-date', get_default_study_shift_session_date, name='default_study_shift_session_date'),
    url('student/register/', student_register, name='student_register'),
    url('reward/detail/', get_reward_by_code, name='reward_detail'),
    url('classes/list-by-centre-course/', get_classes_by_centre_and_course, name='classes_by_centre_course'),
    url('admin/study_shifts_by_date_range_api/', get_study_shifts_by_date_range_api, name='study_shifts_by_date_range_api'),
    url('admin/view_study_shift_schedule/', view_study_shift_schedule, name='view_study_shift_schedule'),
    url('admin/get_classes_api/', get_classes_api, name='get_classes_api'),
    url('admin/get_must_pay_amount_api/', get_must_pay_amount_api, name='get_must_pay_amount_api'),
    url('student/payment-request/state/change/', change_payment_request_state, name='payment_request_state_change'),
    url('admin/html-to-pdf', download_pdf, name='download_pdf'),

    path('admin/dashboard-header-data', get_dashboard_header_data, name='dashboard_header_data'),
    path('admin/fetch-revenue-data', get_revenue_data_api, name='fetch_revenue_data'),
    path('admin/users-chart-data-api', get_users_chart_data_api, name='users-chart-data-api'),
    path('admin/students-chart-data-api', get_students_chart_data_api, name='students-chart-data-api'),
    path('admin/study-shift-chart-data-api', get_study_shift_chart_data_api, name='students-chart-data-api'),
    path('admin/password_reset/', reset_password,name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

admin.site.site_header = 'Quản lý trung tâm'
admin.site.site_title = 'Quản lý thông tin'
admin.site.index_title = 'Quản lý thông tin'
admin.site.site_url = '/admin'

admin.site.login = CustomAdminSite.login
