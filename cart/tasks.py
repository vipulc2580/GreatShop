from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from accounts.models import User

@shared_task
def send_bulk_notification(request,mail_subject,htmlfile,context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(f'accounts/emails/{htmlfile}', context)
    users=User.objects.all()
    to_emails=[]
    if users:
        to_emails=[user.email for user in users]
    mail = EmailMessage(mail_subject, message, from_email, bcc=to_emails)
    mail.content_subtype = "html"  # Ensures email is sent as HTML
    mail.send()
