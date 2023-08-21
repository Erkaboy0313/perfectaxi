from django.db.models import Manager,Sum


class SeriviseManger(Manager):

    def sumSerivies(self,service_list):
        if service_list:
            res = self.get_queryset().filter(id__in = service_list).aggregate(tottal = Sum('cost'))
            return res.get('tottal')
        else:
            return 0