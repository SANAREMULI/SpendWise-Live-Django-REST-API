from rest_framework import serializers

from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'amount', 'description', 'category', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']