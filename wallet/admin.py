from django.contrib import admin

from .models import Wallet, Operation


# Регистрация модели кошелька в админке
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    # Отображаемые поля
    list_display = (
        'wallet_uuid',
        'balance',
    )
    # Поля для поиска
    search_fields = (
        'wallet_uuid',
    )


# Регистрация модели операции в админке
@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    # Отображаемые поля
    list_display = (
        'wallet',
        'operation_type',
        'amount',
        'created_at',
    )
    # Поля для поиска
    search_fields = (
        'wallet__wallet_uuid',
        'operation_type',
        'amount',
        'created_at',
    )
    # Фильтры в списке объектов
    list_filter = (
        'wallet',
        'operation_type',
        'amount',
        'created_at',
    )
    # Сортировка по умолчанию
    ordering = (
        '-created_at',
    )


class InsufficantFundsError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'{self.message}'
        else:
            return 'InsufficientFundsError, Недостаточно средств на балансе'

