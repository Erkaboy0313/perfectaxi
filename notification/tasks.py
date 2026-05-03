from celery import shared_task
from notification.utils import send_notifications_to_tokens


@shared_task(name='send_push_notification')
def send_push_notification(tokens, title, body):
    return send_notifications_to_tokens(tokens, title, body)
