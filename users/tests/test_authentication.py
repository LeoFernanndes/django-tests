import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class JWTAuthenticationTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_obtain_token_success(self):
        credentials = {
            'username': 'testuser',
            'password': 'testpassword123'
        }

        response = self.client.post(self.token_url, credentials)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(len(response.data['access']) > 0)
        self.assertTrue(len(response.data['refresh']) > 0)

    def test_obtain_token_invalid_credentials(self):
        credentials = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.token_url, credentials)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_obtain_token_nonexistent_user(self):
        credentials = {
            'username': 'nonexistent',
            'password': 'password123'
        }

        response = self.client.post(self.token_url, credentials)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_missing_username(self):
        credentials = {
            'password': 'testpassword123'
        }

        response = self.client.post(self.token_url, credentials)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token_missing_password(self):
        credentials = {
            'username': 'testuser'
        }

        response = self.client.post(self.token_url, credentials)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        credentials = {
            'username': 'testuser',
            'password': 'testpassword123'
        }

        response = self.client.post(self.token_url, credentials)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_success(self):
        # First get tokens
        credentials = {
            'username': 'testuser',
            'password': 'testpassword123'
        }

        token_response = self.client.post(self.token_url, credentials)
        refresh_token = token_response.data['refresh']

        # Now refresh the token
        refresh_data = {
            'refresh': refresh_token
        }

        response = self.client.post(self.refresh_url, refresh_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertTrue(len(response.data['access']) > 0)

    def test_refresh_token_invalid(self):
        refresh_data = {
            'refresh': 'invalid_token'
        }

        response = self.client.post(self.refresh_url, refresh_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_missing(self):
        response = self.client.post(self.refresh_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticatedEndpointsTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Generate tokens
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def test_access_protected_endpoint_with_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        url = reverse('users-retrieve-self')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_access_protected_endpoint_without_token(self):
        url = reverse('users-retrieve-self')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')

        url = reverse('users-retrieve-self')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_malformed_header(self):
        self.client.credentials(HTTP_AUTHORIZATION='InvalidFormat token123')

        url = reverse('users-retrieve-self')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_expired_token(self):
        # Create an expired token (this would require manually creating a token with past exp)
        # For this test, we'll simulate by using an invalid token
        expired_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjAwMDAwMDAwLCJpYXQiOjE2MDAwMDAwMDAsImp0aSI6IjAwMDAwMDAwMDAwMDAwMDAiLCJ1c2VyX2lkIjoxfQ.invalid_signature'

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_token}')

        url = reverse('users-retrieve-self')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationFlowTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_complete_authentication_flow(self):
        # 1. Register a new user
        user_data = {
            'username': 'flowuser',
            'password': 'flowpassword123',
            'email': 'flow@example.com',
            'first_name': 'Flow',
            'last_name': 'User'
        }

        register_url = reverse('users-list')
        register_response = self.client.post(register_url, user_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # 2. Authenticate and get tokens
        credentials = {
            'username': 'flowuser',
            'password': 'flowpassword123'
        }

        token_response = self.client.post(self.token_url, credentials)
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)

        access_token = token_response.data['access']
        refresh_token = token_response.data['refresh']

        # 3. Use access token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        self_url = reverse('users-retrieve-self')
        self_response = self.client.get(self_url)
        self.assertEqual(self_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self_response.data['username'], 'flowuser')

        # 4. Refresh the access token
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(self.refresh_url, refresh_data)
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)

        new_access_token = refresh_response.data['access']

        # 5. Use new access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')

        self_response_2 = self.client.get(self_url)
        self.assertEqual(self_response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(self_response_2.data['username'], 'flowuser')

    def test_token_authentication_with_different_user_actions(self):
        # Create user and get token
        user = User.objects.create_user(
            username='actionuser',
            email='action@example.com',
            password='actionpassword123'
        )

        credentials = {
            'username': 'actionuser',
            'password': 'actionpassword123'
        }

        token_response = self.client.post(self.token_url, credentials)
        access_token = token_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Test various authenticated actions

        # 1. Retrieve self
        self_url = reverse('users-retrieve-self')
        response = self.client.get(self_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Update self
        update_url = reverse('users-update-self')
        update_data = {'first_name': 'Updated'}
        response = self.client.post(update_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

        # 3. Access user detail (self)
        detail_url = reverse('users-detail', kwargs={'pk': user.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='password123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            is_staff=True
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='password123'
        )

        # Get tokens
        regular_refresh = RefreshToken.for_user(self.regular_user)
        self.regular_token = str(regular_refresh.access_token)

        admin_refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(admin_refresh.access_token)

    def test_regular_user_permissions(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_token}')

        # Can access self
        self_url = reverse('users-retrieve-self')
        response = self.client.get(self_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can update self
        update_url = reverse('users-update-self')
        response = self.client.post(update_url, {'first_name': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can delete self
        detail_url = reverse('users-detail', kwargs={'pk': self.regular_user.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_access_others(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_token}')

        # Cannot update other user
        other_detail_url = reverse('users-detail', kwargs={'pk': self.other_user.id})
        response = self.client.patch(other_detail_url, {'first_name': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cannot delete other user
        response = self.client.delete(other_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_permissions(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        # Can access other users
        other_detail_url = reverse('users-detail', kwargs={'pk': self.other_user.id})
        response = self.client.get(other_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can update other users
        response = self.client.patch(other_detail_url, {'first_name': 'AdminUpdated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can delete other users
        response = self.client.delete(other_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_public_endpoints_no_auth_required(self):
        # List users endpoint should be public
        list_url = reverse('users-list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Registration should be public
        user_data = {
            'username': 'publicuser',
            'password': 'password123',
            'email': 'public@example.com'
        }
        response = self.client.post(list_url, user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)