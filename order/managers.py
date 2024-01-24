from django.db.models import Manager,Sum,F
from django.db.models.functions import TruncDate,ExtractWeekDay
from django.utils import timezone

class SeriviseManger(Manager):

    async def sumSerivies(self,service_list):
        if service_list:
            res = await self.filter(id__in = service_list).aaggregate(tottal = Sum('cost'))
            return res.get('tottal')
        else:
            return 0


class DriverHistoryManager(Manager):
    
    def get_last_7_days_report(self,user):
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=7)

        report = (
            self.filter(driver__user=user, time__gte=start_date)
            .annotate(order_date=TruncDate('time'), weekday=ExtractWeekDay('time'))
            .values('order_date', 'weekday')
            .annotate(total_earned=Sum(F('order__price')))
            .order_by('order_date')
            )

        return report