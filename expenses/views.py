from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Expense
from .serializers import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
	serializer_class = ExpenseSerializer
	permission_classes = [IsAuthenticated]
	filterset_fields = ['category']
	search_fields = ['description']
	ordering_fields = ['amount', 'created_at']

	def get_queryset(self):
		return Expense.objects.filter(owner=self.request.user)

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)
