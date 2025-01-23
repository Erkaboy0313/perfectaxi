from celery import shared_task
from .models import Feedback
from django.db.models import Avg
from users.models import Driver


@shared_task(name = 'populateDefaultMark')
def populate_mark(driver_id):
    # need to add 50 reviews to driver in the beginning.
    pass


@shared_task(name = 'calculateMark')
def calculate_mark(driver_id):
    driver = Driver.objects.get(id = driver_id)
    average = Feedback.objects.filter(order__driver = driver)[:150].aggregate(average = Avg('mark'))['average']
    driver.mark = round(average,1)
    driver.save()