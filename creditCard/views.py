from users.permissions import IsActive
from rest_framework import viewsets,response,status
from .models import Card
from .serializers import CreditCardSerializer
from rest_framework.decorators import action
from PerfectTaxi.exceptions import BaseAPIException
from users.models import Client

class CardView(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CreditCardSerializer
    permission_classes = (IsActive,)
    http_method_names = ['get','post']

    def perform_create(self, serializer):
        try:
            user = Client.objects.get(user = self.request.user)
        except:
            raise BaseAPIException('user should be client instance')
        serializer.save(user = user)

    @action(detail=True,methods=["post"])
    def verify(self,request,pk=None):
        card = Card.objects.get(id = pk)
        card.verified = True
        card.save()
        return response.Response({"messgae":"verified"},status=status.HTTP_200_OK)


    def list(self, request, *args, **kwargs):
        if request.user.role == 'client':
            card = Card.objects.filter(user__user = request.user).first()
            serializer = self.serializer_class(card)
            return response.Response(serializer.data,status=status.HTTP_200_OK)
        elif request.user.role == 'admin':
            return super().list(request,*args,**kwargs)
        else:
            raise BaseAPIException('method not allowed')        



# Create your views here.

