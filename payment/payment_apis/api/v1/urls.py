from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("transaction", views.TransactionViewSet, basename="transaction")

urlpatterns = router.urls
