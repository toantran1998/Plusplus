from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EmailInbox(models.Model):
    subject = models.CharField(_('Tiêu đề'), max_length=255)
    # centre = models.ForeignKey('centre.Centre', on_delete=models.PROTECT, verbose_name=_('Trung tâm'), default=None)
    # from_user = models.ForeignKey('user.AuthUser', on_delete=models.PROTECT, related_name='from_user_email_set',
    #                               verbose_name=_('Người gửi'))
    # to_users = models.ManyToManyField('user.AuthUser', related_name='to_users_email', verbose_name=_('Người nhận'))
    from_email = models.EmailField(_('Người gửi'), default=None)
    to_email = models.EmailField(_('Người nhận'), default=None)
    content = models.TextField(_('Nội dung'))
    # files = models.FilePathField(_('File đính kèm'), default=None, null=True)
    sent_date_time = models.DateTimeField(_('Ngày gửi'), null=True, blank=True, editable=False, auto_now_add=True)
    state = models.IntegerField(_('Trạng thái'), null=True, blank=True,
                                choices=[(0, 'Chưa gửi'), (1, 'Gửi thành công'), (2, 'Gửi thất bại')], default=0)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='emailinbox_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='emailinbox_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'email_inbox'
        verbose_name = _("Email")
        verbose_name_plural = _('Email')
        app_label = 'message'

    def __str__(self):
        return self.subject


class Notification(models.Model):
    title = models.CharField(_('Tiêu đề'), max_length=255)
    # from_user = models.ForeignKey('user.AuthUser', on_delete=models.PROTECT, related_name='from_user_notify_set',
    #                               verbose_name=_('Người gửi'))
    to_user_id = models.IntegerField(_('Mã người nhận'), default=None)
    content = models.TextField(_('Nội dung'))
    url = models.CharField(_('Url'), max_length=255)
    sent_date = models.DateTimeField(_('Ngày gửi'), null=True, blank=True, editable=False)
    viewed_state = models.BooleanField(_('Đã đọc'), default=False, editable=False)
    # state = models.IntegerField(_('Trạng thái'), null=True, blank=True,
    #                             choices=[(0, 'Chưa gửi'), (1, 'Gửi thành công'), (2, 'Gửi thất bại')], default=0)
    created_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, related_name='notification_create_user_set',
                                     on_delete=models.PROTECT,  verbose_name=_('Người tạo'))
    updated_user = models.ForeignKey('user.AuthUser', default=None, null=True, blank=True, editable=False, related_name='notification_update_user_set',
                                     on_delete=models.PROTECT, verbose_name=_('Người cập nhật'))
    created_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)
    updated_date_time = models.DateTimeField(null=True, default=timezone.now, editable=False)

    class Meta:
        managed = True
        db_table = 'notification'
        verbose_name = _("Thông báo")
        verbose_name_plural = _('Thông báo')
        app_label = 'message'
        ordering = ['viewed_state']

    def __str__(self):
        return self.title
