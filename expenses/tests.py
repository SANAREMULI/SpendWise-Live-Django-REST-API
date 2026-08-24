from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Expense


class ExpenseApiTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(username='alice', password='password123')
		self.other_user = user_model.objects.create_user(username='bob', password='password123')
		self.token = Token.objects.create(user=self.user)
		self.other_token = Token.objects.create(user=self.other_user)
		self.url = '/api/expenses/'

	def authenticate(self, token):
		self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

	def test_login_returns_token(self):
		response = self.client.post('/api/login/', {'username': 'alice', 'password': 'password123'})
		self.assertEqual(response.status_code, 200)
		self.assertIn('token', response.data)

	def test_unauthenticated_requests_are_rejected(self):
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, 401)
		self.client.credentials(HTTP_AUTHORIZATION='Token invalid-token')
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, 401)

	def test_expenses_are_scoped_and_owner_is_automatic(self):
		Expense.objects.create(owner=self.other_user, amount='99.00', description='Private', category='other')
		self.authenticate(self.token)
		response = self.client.post(self.url, {'amount': '4.50', 'description': 'Coffee', 'category': 'food', 'owner': self.other_user.pk})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['owner'], self.user.pk)
		listing = self.client.get(self.url)
		self.assertEqual(listing.data['count'], 1)
		self.assertEqual(listing.data['results'][0]['description'], 'Coffee')
		self.authenticate(self.other_token)
		other_listing = self.client.get(self.url)
		self.assertEqual(other_listing.data['count'], 1)
		self.assertEqual(other_listing.data['results'][0]['description'], 'Private')

	def test_filter_search_ordering_and_pagination(self):
		self.authenticate(self.token)
		for index in range(11):
			Expense.objects.create(owner=self.user, amount=index + 1, description=f'Coffee {index}', category='food' if index < 10 else 'travel')
		filtered = self.client.get(self.url, {'category': 'food'})
		self.assertEqual(filtered.data['count'], 10)
		searched = self.client.get(self.url, {'search': 'Coffee 1'})
		self.assertEqual(searched.data['count'], 2)
		ordered = self.client.get(self.url, {'ordering': '-amount'})
		self.assertEqual(ordered.data['results'][0]['amount'], '11.00')
		self.assertIn('next', ordered.data)
		self.assertIn('previous', ordered.data)
		self.assertIn('results', ordered.data)
