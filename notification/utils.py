import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from category.models import Log

FIREBASE_SERVICE_ACCOUNT_JSON = os.path.join(settings.BASE_DIR, 'utils', 'service-account.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_JSON)
    firebase_admin.initialize_app(cred)


def send_notifications_to_tokens(tokens, title, body):
    """Send notification to a list of FCM tokens in batches of 500."""
    results = {'success': 0, 'failure': 0}
    BATCH_SIZE = 500

    for i in range(0, len(tokens), BATCH_SIZE):
        batch_tokens = tokens[i:i + BATCH_SIZE]
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=batch_tokens,
            android=messaging.AndroidConfig(priority='high'),
        )
        resp = messaging.send_each_for_multicast(message, app=firebase_admin.get_app())

        for idx, resp_item in enumerate(resp.responses):
            if not resp_item.success:
                Log.objects.create(
                    text=f"FCM failed token={batch_tokens[idx]} reason={resp_item.exception}"[:100]
                )

        Log.objects.create(
            text=(
                f"FCM batch {i // BATCH_SIZE + 1}: "
                f"{resp.success_count} ok, {resp.failure_count} fail"
            )[:100]
        )
        results['success'] += resp.success_count
        results['failure'] += resp.failure_count

    return results
