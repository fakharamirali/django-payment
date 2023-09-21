from django.urls import path, include

urlpatterns = [
    path("v1/", include('payment.payment_apis.api.v1.urls'))
]
