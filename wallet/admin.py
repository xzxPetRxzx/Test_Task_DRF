from django.contrib import admin

from .models import Wallet, Operation


# Регистрация модели кошелька в админке
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('wallet_uuid', 'balance')  # Отображаемые поля
    search_fields = ('wallet_uuid',)  # Поля для поиска


# Регистрация модели операции в админке
@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'operation_type', 'amount', 'created_at')  # Отображаемые поля
    search_fields = ('wallet__wallet_uuid', 'operation_type', 'amount', 'created_at')  # Поля для поиска
    list_filter = ('wallet', 'operation_type', 'amount', 'created_at')  # Фильтры в списке объектов
    ordering = ('-created_at',)  # Сортировка по умолчанию


class InsufficantFundsError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        print('calling str')
        if self.message:
            return f'InsufficantFundsError, {self.message} '
        else:
            return 'InsufficantFundsError, Недостаточно средств на балансе'

