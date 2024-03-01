from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from tasks.api.views import TaskViewSet

router = SimpleRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
