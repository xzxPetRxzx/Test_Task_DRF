from django.urls import path

from .views import WalletView, WalletOperationView

urlpatterns = [
    path('<uuid:wallet_uuid>/operation', WalletOperationView.as_view()),
    path('<uuid:wallet_uuid>', WalletView.as_view()),
]