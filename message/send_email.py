import csv
import smtplib
from email.mime.text import MIMEText

import requests
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML

from app_config import settings
from app_config.settings import EMAIL_HOST_USER
from message.models import EmailInbox
from user.models import AuthUser

email_address = settings.email_address
email_password = settings.email_password


def create_email_message(to_address, subject, body):
    msg = EmailMessage(subject=subject, from_email=email_address, to=[to_address], body=body)
    msg.content_subtype = "html"
    return msg


def send(to, subject, body, attach_files=None):
    msg = create_email_message(
        to_address=to,
        subject=subject,
        body=body,
    )

    if attach_files:
        for att_file in attach_files:
            msg.attach(att_file['name'], att_file['content'], mimetype=att_file['mimetype'])
    msg.send()
    email = EmailInbox(subject=subject, content=body, from_email='ODIN System', to_email=to, state=1)
    email.save()

    # with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
    #     smtp_server.ehlo()
    #     smtp_server.starttls()
    #     smtp_server.login(email_address, email_password)
    #     smtp_server.send_message(msg)
    #     email = EmailInbox(subject=subject, content=body, from_email='ODIN System', to_email=to, state=1)
    #     email.save()
