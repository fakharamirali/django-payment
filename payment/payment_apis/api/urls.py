from django.urls import include, path

urlpatterns = [
    path("v1/", include('payment.payment_apis.api.v1.urls'))
]
