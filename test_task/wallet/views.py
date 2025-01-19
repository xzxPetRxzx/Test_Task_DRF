from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .admin import InsufficantFundsError
from .models import Wallet, Operation
from .serialisers import WalletSerializer, OperationSerializer


# View для запроса состояния кошелька
class WalletView(APIView):
    # GET запрос(берет идентификатор кошелька из запроса)
    @staticmethod
    def get(request, wallet_uuid):
        # Пытаемся получить кошелек, если найден возвращаем ответ,
        # если не найден ловим ошибку
        try:
            wallet = Wallet.objects.get(wallet_uuid=wallet_uuid)
            serializer = WalletSerializer(wallet)
            return Response(serializer.data)
        # Ловим ошибку DoesNotExist, возвращаем ответ и статус 404
        except Wallet.DoesNotExist:
            return Response(data={'error': 'Кошелек не найден'},
                            status=status.HTTP_404_NOT_FOUND)


# View для операций с кошельком
class WalletOperationView(APIView):
    # Post запрос для выполнения операций с кошельком
    @staticmethod
    def post(request, wallet_uuid):
        serializer = OperationSerializer(data=request.data)
        # Не валидный json
        if not serializer.is_valid():
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        # Пробуем обработать запрос:
        try:
            # Получаем кошелек для изменения(если не найден ловим ошибку)
            wallet = Wallet.objects.get(wallet_uuid=wallet_uuid)
            operation_type = serializer.validated_data['operationType']
            amount = serializer.validated_data['amount']
            # Проверяем тип операции DEPOSIT или WITHDRAW
            if operation_type == 'DEPOSIT':
                # При депозите кладем средства
                wallet.change_balance(amount)
            else:
                # При снятии проверяем достаточно ли средств на балансе. Если достаточно снимаем
                if wallet.balance >= amount:
                    wallet.change_balance(-amount)
            # Если недостаточно ловим ошибку
                else:
                    raise InsufficantFundsError('Недостаточно средств')
                    # Создаем операцию, обновляем кошелек из БД
            operation = Operation.objects.create(wallet=wallet,
                                                 operation_type=operation_type,
                                                 amount=amount)
            wallet.refresh_from_db()
            # Возвращаем успешное выполнение
            return Response(data={'wallet_uuid': wallet.wallet_uuid,
                                  'operation': operation.operation_type,
                                  'amount': operation.amount,
                                  'balance': wallet.balance},
                            status=status.HTTP_200_OK)

        # Кошелька не существует
        except Wallet.DoesNotExist:
            return Response(data={'error': 'Кошелька не существует'},
                            status=status.HTTP_404_NOT_FOUND)
        # Недостаточно средств на балансе(дописать класс ошибки)
        except InsufficantFundsError as e:
             return Response(data={'error': str(e)},
                             status=status.HTTP_400_BAD_REQUEST)
        # Все остальные ошибки
        except Exception as e:
            return Response(data={'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)