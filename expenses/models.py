from django.db import models


class Expense(models.Model):
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	description = models.CharField(max_length=255)
	category = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='expenses')

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.description} ({self.amount})'
