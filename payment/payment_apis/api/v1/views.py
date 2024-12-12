import logging

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from payment.models import Transaction
from payment.status import StatusChoices
from ... import serializers

logger = logging.getLogger(__name__)


class TransactionViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = [
        IsAuthenticated
    ]
    serializer_class = serializers.TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    @action(detail=True, url_path="verify", url_name="verify")
    def verify(self, request, *args, **kwargs):
        obj: Transaction = self.get_object()
        prev_status = obj.status
        obj.verify()
        if prev_status != obj.status == StatusChoices.SUCCESSFUL:
            if obj.linked_contenttype is not None:
                if hasattr(obj.linked_contenttype.model_class(), "on_transaction_successful") and callable(
                        obj.linked_contenttype.model_class().on_transaction_successful):
                    try:
                        obj.linked_contenttype.model_class().on_transaction_successful(transaction=obj, request=request)
                    except Exception as e:
                        logger.warning(str(e), exc_info=True)

        return self.retrieve(request, *args, **kwargs)
