import uuid
from django.db import models


# Модель кошелька
class Wallet(models.Model):
    # UUID кошелька
    wallet_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Баланс кошелька
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    # Изменение баланса
    def change_balance(self, amount):
        self.balance += amount
        self.save()


# Модель операций(истории операций)
class Operation(models.Model):
    # Подкласс для выбора вариантов операции
    class OperationType(models.TextChoices):
        # Положить деньги на баланс
        DEPOSIT = 'DEPOSIT'
        # Снять деньги с баланса
        WITHDRAW = 'WITHDRAW'
    # Ссылка на кошелек
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='operations')
    # Тип операции(выбор положить/снять)
    operation_type = models.CharField(max_length=8, choices=OperationType.choices)
    # Сумма операции
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    # Время операции
    created_at = models.DateTimeField(auto_now_add=True)
