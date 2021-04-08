# Generated by Django 3.1.7 on 2021-03-31 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('message', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='created_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='notification_create_user_set', to=settings.AUTH_USER_MODEL, verbose_name='Người tạo'),
        ),
        migrations.AddField(
            model_name='notification',
            name='updated_user',
            field=models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='notification_update_user_set', to=settings.AUTH_USER_MODEL, verbose_name='Người cập nhật'),
        ),
        migrations.AddField(
            model_name='emailinbox',
            name='created_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='emailinbox_create_user_set', to=settings.AUTH_USER_MODEL, verbose_name='Người tạo'),
        ),
        migrations.AddField(
            model_name='emailinbox',
            name='updated_user',
            field=models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='emailinbox_update_user_set', to=settings.AUTH_USER_MODEL, verbose_name='Người cập nhật'),
        ),
    ]
