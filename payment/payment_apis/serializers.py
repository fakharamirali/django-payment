from rest_framework import serializers

from payment.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    redirect_url = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_id',
            'amount',
            'card_holder',
            'shaparak_tracking_code',
            'status',
            'description',
            # Important times
            'create_date',
            'create_transaction_at',
            'last_verify',
            'last_edit',
            'redirect_url',
        ]

    @staticmethod
    def get_redirect_url(obj: Transaction):
        return obj.get_redirect_url()
