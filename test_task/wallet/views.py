from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Wallet
from .serialisers import WalletSerializer


# View для запроса состояния кошелька
class WalletView(APIView):
    # GET запрос(берет идентификатор кошелька из запроса)
    def get(self, request, wallet_uuid):
        # Пытаемся получить кошелек, если найден возвращаем ответ,
        # если не найден ловим ошибку
        try:
            wallet = Wallet.objects.get(wallet_uuid=wallet_uuid)
            serializer = WalletSerializer(wallet)
            return Response(serializer.data)
        # Ловим ошибку DoesNotExist, возвращаем ответ и статус 404
        except Wallet.DoesNotExist:
            return Response({'error': 'Кошелек не найден'}, status=status.HTTP_404_NOT_FOUND)
