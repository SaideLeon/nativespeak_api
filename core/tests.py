from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class BasicTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_login_and_goal_crud(self):
        # Register
        resp = self.client.post('/api/register/', {'username':'testuser','email':'t@example.com','password':'1234'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Obtain token
        resp = self.client.post('/api/token/', {'username':'testuser','password':'1234'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        access = resp.data.get('access')

        # Create goal
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        resp = self.client.post('/api/goals/', {'text':'Aprender inglês 30 minutos'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
