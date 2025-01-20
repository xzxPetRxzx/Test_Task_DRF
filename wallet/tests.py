from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from wallet.models import Wallet

# Класс тестов
class WalletAPITest(APITestCase):

    # Первоначальные настройки тестов
    def setUp(self):
        # Тестовый UUID для создания тестового кошелька в БД
        self.wallet_uuid = 'df553847-3ae6-4927-a48d-2b90fc90e08e'
        # Генерация URL для теста существующего кошелька
        self.deposit_url = reverse(
            viewname='wallet_operation',
            kwargs={'wallet_uuid': self.wallet_uuid}
        )
        self.balance_url = reverse(
            viewname='wallet_balance',
            kwargs={'wallet_uuid': self.wallet_uuid}
        )
        # Создаем тестовый кошелек в базе данных
        self.wallet = Wallet.objects.create(
            wallet_uuid=self.wallet_uuid,
            balance=1000
        )
        # Отсутствующий в базе тестовый UUID
        self.fake_wallet_uuid = '579189f8-8112-45bf-a7f3-ee274d7c8d1b'
        # Генерация URL для теста отсутствующего кошелька
        self.fake_deposit_url = reverse(
            viewname='wallet_operation',
            kwargs={'wallet_uuid': self.fake_wallet_uuid}
        )
        self.fake_balance_url = reverse(
            viewname='wallet_balance',
            kwargs={'wallet_uuid': self.fake_wallet_uuid}
        )

    # Тест запроса баланса
    def test_get_wallet_balance_success(self):
        response = self.client.get(self.balance_url)
        answer = {
            "wallet_uuid": self.wallet_uuid,
            "balance": f'{self.wallet.balance:.2f}'
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), answer)

    # Тест запроса баланса несуществующего кошелька
    def test_get_wallet_not_found(self):
        response = self.client.get(self.fake_balance_url)
        answer = {
            'error': 'Кошелек не найден'
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), answer)

    # Тест начисления денег на баланс
    def test_post_operation_deposit_success(self):
        question = {
            "operationType": "DEPOSIT",
            "amount": '500.00'
        }
        balance = self.wallet.balance
        response = self.client.post(self.deposit_url, question, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        answer = {
            'wallet_uuid': self.wallet_uuid,
            'operation': 'DEPOSIT',
            'amount': '500.00',
            'balance': f'{self.wallet.balance:.2f}'
        }
        self.assertEqual(self.wallet.balance, balance + 500)
        self.assertEqual(response.json(), answer)

    # Тест начисления денег на баланс для несуществующего кошелька
    def test_post_operation_not_found(self):
        question = {
            "operationType": "DEPOSIT",
            "amount": '500.0'
        }
        response = self.client.post(self.fake_deposit_url, question, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        answer = {'error': 'Кошелек не найден'}
        self.assertEqual(response.json(), answer)

    # Тест снятия среств с кошелька
    def test_post_operation_withdraw_success(self):
        question = {
            "operationType": "WITHDRAW",
            "amount": '300'
        }
        balance = self.wallet.balance
        response = self.client.post(self.deposit_url, question, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        answer = {
            'wallet_uuid': self.wallet_uuid,
            'operation': 'WITHDRAW',
            'amount': '300.00',
            'balance': f'{self.wallet.balance:.2f}'
        }
        self.assertEqual(self.wallet.balance, balance - 300)
        self.assertEqual(response.json(), answer)

    # Тест снятия средств с кошелька при недостаточном балансе
    def test_post_operation_withdraw_insufficient_funds(self):
        question = {
            "operationType": "WITHDRAW",
            "amount": '100000'  # Больше, чем баланс
        }
        answer = {'error': 'Недостаточно средств'}
        balance = self.wallet.balance
        response = self.client.post(self.deposit_url, question, format='json')
        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.wallet.balance, balance)
        self.assertEqual(response.json(),answer)

    # Тест обработки некорректного json
    def test_post_operation_incorrect_json(self):
        question = {
            "operationType": "DT",
            "amount": '500'
        }
        balance = self.wallet.balance
        response = self.client.post(self.deposit_url, question, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.wallet.refresh_from_db()
        answer = {'error': 'Неверный запрос'}
        self.assertEqual(self.wallet.balance, balance)
        self.assertEqual(response.json(), answer)