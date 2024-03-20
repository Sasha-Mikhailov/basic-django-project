from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from billing.api.views import TransactionViewSet

router = SimpleRouter()
router.register("payments", TransactionViewSet, basename="transactions")

urlpatterns = [
    path("", include(router.urls)),
]
