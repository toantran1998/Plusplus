from django.contrib.admin import AdminSite
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from app_config import settings


class CustomAdminSite(AdminSite):
    @never_cache
    def login(self, request, extra_context=None):
        """
        Displays the login form for the given HttpRequest.
        """
        context = {
            'title': 'Đăng nhập',
            'app_path': request.get_full_path(),
            REDIRECT_FIELD_NAME: settings.LOGIN_REDIRECT_URL,
        }
        context.update(extra_context or {})

        defaults = {
            'extra_context': context,
            'current_app': self.name,
            'authentication_form': self.login_form or AdminAuthenticationForm,
            'template_name': self.login_template or 'admin/login.html',
        }
        return login(request, **defaults)

    @never_cache
    def index(self, request, extra_context=None):
        app_list = self.get_app_list(request)

        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            **(extra_context or {}),
        }

        request.current_app = self.name

        # Neu user la super admin, le tan hoac nhan vien kinh doanh#
        if request.user.is_superuser or request.user.groups_id == 1 or request.user.groups_id == 6:
            return TemplateResponse(request, self.index_template or 'admin/index.html', context)
        return TemplateResponse(request, self.index_template or 'admin/index.html', context)

site = CustomAdminSite()