from django.urls import path

from .views import WalletView

urlpatterns = [
    path('<uuid:wallet_uuid>', WalletView.as_view()),
#   path('<uuid:wallet_uuid>/operation', as_view())
]