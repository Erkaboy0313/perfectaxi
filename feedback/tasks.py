from celery import shared_task
from .models import Feedback
from django.db.models import Avg
from users.models import Driver


@shared_task(name = 'populateDefaultMark')
def populate_mark(driver_id):
    driver = Driver.objects.get(id = driver_id)
    default_marks = []
    for _ in range(50):
        mark = Feedback(driver = driver,mark = 5)
        default_marks.append(mark)
    Feedback.objects.bulk_create(default_marks)
    driver.generated_default_mark = True
    driver.save()


@shared_task(name = 'calculateMark')
def calculate_mark(driver_id):
    driver = Driver.objects.get(id = driver_id)
    average = Feedback.objects.filter(driver = driver)[:150].aggregate(average = Avg('mark'))['average']
    driver.mark = round(average,1)
    driver.save()