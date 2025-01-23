from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Wallet, Operation
from .serialisers import WalletSerializer, OperationSerializer


# View для запроса состояния кошелька
class WalletView(APIView):
    def get(self, request, wallet_uuid):
        try:
            wallet = Wallet.objects.get(wallet_uuid=wallet_uuid)
            serializer = WalletSerializer(wallet)
            return Response(serializer.data)
        except Wallet.DoesNotExist:
            return Response(
                data={'error': 'Кошелек не найден'},
                status=status.HTTP_404_NOT_FOUND
            )


# View для операций с кошельком
class WalletOperationView(APIView):
    def post(self, request, wallet_uuid):
        serializer = OperationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                data={'error': 'Неверный запрос'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(wallet_uuid=wallet_uuid)
                operation_type = serializer.validated_data['operationType']
                amount = serializer.validated_data['amount']
                if operation_type == 'WITHDRAW' and wallet.balance < amount:
                    return Response(
                        data={'error': 'Недостаточно средств'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if operation_type == 'DEPOSIT':
                    wallet.balance = F('balance') + amount
                else:
                    wallet.balance = F('balance') - amount
                wallet.save()
                wallet.refresh_from_db()
                operation = Operation.objects.create(
                    wallet=wallet,
                    operation_type=operation_type,
                    amount=amount
                )
                return Response(
                    data={
                        'wallet_uuid': wallet.wallet_uuid,
                        'operation': operation.operation_type,
                        'amount': f'{operation.amount:.2f}',
                        'balance': f'{wallet.balance:.2f}'
                    },
                    status=status.HTTP_200_OK)
        # Кошелек не найден
        except Wallet.DoesNotExist:
            return Response(
                data={'error': 'Кошелек не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        # Все остальные ошибки
        except Exception as e:
            return Response(
                data={'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )