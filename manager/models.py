
from django.contrib.auth.models import Group, AbstractUser, Permission
from django.db import models
from django.utils import timezone



# class Revenue(BaseModel):
#     title = models.CharField(_('Tiêu đề'), max_length=255)
#     centre = models.ForeignKey(Centre, on_delete=models.PROTECT, verbose_name=_('Trung tâm'), default=None)
#     user = models.OneToOneField(AuthUser, on_delete=models.PROTECT, verbose_name=_('Người nộp'), null=True, default=None)
#     amount = models.IntegerField(_('Số tiền (VNĐ)'))
#     input_date = models.DateField(_('Ngày thu'), default=None)
#     note = models.CharField(_("Ghi chú"), max_length=255, default=None, null=True, blank=True)
#
#     class Meta:
#         managed = True
#         db_table = 'revenues'
#         verbose_name = _("Doanh thu")
#         verbose_name_plural = _('Doanh thu')
#         app_label = 'manager'
#
#     def __str__(self):
#         return self.title

