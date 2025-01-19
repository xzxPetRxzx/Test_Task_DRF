from rest_framework import serializers
from .models import Wallet, Operation


# Сериалайзер операции
class OperationSerializer(serializers.Serializer):
    operationType = serializers.ChoiceField(choices=Operation.OperationType.choices)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)


# Сериалайзер кошелька
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['wallet_uuid', 'balance']