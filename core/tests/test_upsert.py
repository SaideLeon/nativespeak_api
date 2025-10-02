from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class UpsertTests(APITestCase):
    def setUp(self):
        # create a user and obtain JWT access token for authenticated endpoints
        self.user = User.objects.create_user(username='tester', password='testpass')
        token_resp = self.client.post('/api/token/', {'username': 'tester', 'password': 'testpass'}, format='json')
        assert token_resp.status_code == status.HTTP_200_OK, f"token obtain failed: {token_resp.status_code} {token_resp.data}"
        self.access = token_resp.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_settings_upsert_and_list(self):
        url = reverse('settings-upsert')
        payload = {'key': 'test.setting', 'value': {'foo': 'bar'}}

        # upsert (create)
        resp = self.client.put(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('id', resp.data)
        self.assertEqual(resp.data['key'], payload['key'])
        self.assertEqual(resp.data['value'], payload['value'])

        # list by query param
        list_url = reverse('settings-list') + f'?key={payload["key"]}'
        resp2 = self.client.get(list_url, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp2.data, list)
        self.assertGreaterEqual(len(resp2.data), 1)
        self.assertEqual(resp2.data[0]['key'], payload['key'])

        # upsert (update)
        new_value = {'foo': 'baz', 'n': 2}
        payload2 = {'key': payload['key'], 'value': new_value}
        resp3 = self.client.put(url, payload2, format='json')
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        self.assertEqual(resp3.data['value'], new_value)

    def test_uistate_upsert_and_list(self):
        url = reverse('ui-state-upsert')
        payload = {'key': 'ui.test', 'state': {'cursor': 1}}

        # create via POST
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('id', resp.data)
        self.assertEqual(resp.data['key'], payload['key'])
        self.assertEqual(resp.data['state'], payload['state'])

        # list
        list_url = reverse('ui-state-list') + f'?key={payload["key"]}'
        resp2 = self.client.get(list_url, format='json')
        # our list view currently ignores key param but should return list
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp2.data, list)
        self.assertGreaterEqual(len(resp2.data), 1)
        self.assertEqual(resp2.data[0]['key'], payload['key'])
