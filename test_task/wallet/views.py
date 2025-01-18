from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Wallet
from .serialisers import WalletSerializer, OperationSerializer


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
            return Response(data={'error': 'Кошелек не найден'}, status=status.HTTP_404_NOT_FOUND)


# View для операций с кошельком
class WalletOperationView(APIView):
    # Post запрос для выполнения операций с кошельком
    def post(self, request, wallet_uuid):
        serializer = OperationSerializer(data=request.data)
        # Не валидный json
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # Пробуем обработать запрос:
        try:
            # Получаем кошелек для изменения(если не найден ловим ошибку)
            wallet = Wallet.objects.select_for_update().get(wallet_uuid=wallet_uuid)

            # Проверяем тип операции DEPOSIT или WITHDRAW
            # При депозите ложим средства
            # При снятии проверяем досточно ли средств на балансе
            # Если достаточно снимаем
            # Возвращаем успешное выполнение и обновленым кошелька

        # Кошелька не существует
        except Wallet.DoesNotExist:
            return Response(data={'error': 'Кошелька не существует'}, status=status.HTTP_404_NOT_FOUND)
        # Недостаточно средств на балансе(дописать класс ошибки)
        # except InsufficantFundsOnBallance:
        #     return Response(data={'error': 'Недостаточно средств на балансе'}, status=status.HTTP_400_BAD_REQUEST)
        # Все остальные ошибки
        except Exception as e:
            return Response(data={'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)