import uuid
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class UserRegistrationTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('users-list')

    def test_create_user_success(self):
        user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['username'], user_data['username'])
        self.assertEqual(response.data['email'], user_data['email'])
        self.assertEqual(response.data['first_name'], user_data['first_name'])
        self.assertEqual(response.data['last_name'], user_data['last_name'])
        self.assertNotIn('password', response.data)

        # Verify user was created in database
        user = User.objects.get(username=user_data['username'])
        self.assertEqual(user.email, user_data['email'])
        self.assertTrue(user.check_password(user_data['password']))
        self.assertTrue(isinstance(user.id, uuid.UUID))

    def test_create_user_duplicate_username(self):
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )

        user_data = {
            'username': 'existinguser',
            'password': 'newpassword123',
            'email': 'new@example.com'
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_create_user_duplicate_email(self):
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )

        user_data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'existing@example.com'
        }

        response = self.client.post(self.register_url, user_data)

        # Note: Django User model doesn't enforce unique emails by default
        # This test verifies the current behavior - email duplication is allowed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # If you want to enforce unique emails, you would need to add validation
        # in the serializer or model, then this test would expect 400

    def test_create_user_missing_required_fields(self):
        user_data = {
            'username': 'testuser'
            # Missing password and email
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_create_user_invalid_email(self):
        user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'invalid-email'
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserUpdateTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword123',
            is_staff=True
        )

        # Get JWT token for user
        refresh = RefreshToken.for_user(self.user)
        self.user_token = str(refresh.access_token)

        # Get JWT token for admin
        admin_refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(admin_refresh.access_token)

    def test_update_self_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'main_profile_image_url': 'https://example.com/image.jpg'
        }

        url = reverse('users-update-self')
        response = self.client.post(url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], update_data['first_name'])
        self.assertEqual(response.data['last_name'], update_data['last_name'])
        self.assertEqual(response.data['main_profile_image_url'], update_data['main_profile_image_url'])

        # Verify database update
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, update_data['first_name'])
        self.assertEqual(self.user.last_name, update_data['last_name'])

    def test_update_self_unauthorized(self):
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }

        url = reverse('users-update-self')
        response = self.client.post(url, update_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_self_cannot_change_restricted_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        update_data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'is_staff': True,
            'is_active': False
        }

        url = reverse('users-update-self')
        response = self.client.post(url, update_data)

        # Should succeed but ignore restricted fields
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify restricted fields weren't changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)

    def test_admin_update_other_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        update_data = {
            'first_name': 'Admin Updated',
            'last_name': 'Name'
        }

        url = reverse('users-detail', kwargs={'pk': self.user.id})
        response = self.client.patch(url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], update_data['first_name'])

        # Verify database update
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, update_data['first_name'])

    def test_user_cannot_update_other_user(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        update_data = {
            'first_name': 'Hacker'
        }

        url = reverse('users-detail', kwargs={'pk': other_user.id})
        response = self.client.patch(url, update_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserDeleteTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword123',
            is_staff=True
        )

        # Get JWT tokens
        refresh = RefreshToken.for_user(self.user)
        self.user_token = str(refresh.access_token)

        admin_refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(admin_refresh.access_token)

    def test_admin_delete_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        url = reverse('users-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify user was deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.user.id)

    def test_user_delete_self(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        url = reverse('users-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify user was deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.user.id)

    def test_user_cannot_delete_other_user(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        url = reverse('users-detail', kwargs={'pk': other_user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify user still exists
        self.assertTrue(User.objects.filter(id=other_user.id).exists())

    def test_delete_user_unauthorized(self):
        url = reverse('users-detail', kwargs={'pk': self.user.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Verify user still exists
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_delete_nonexistent_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        fake_id = uuid.uuid4()
        url = reverse('users-detail', kwargs={'pk': fake_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserRetrieveTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )

        refresh = RefreshToken.for_user(self.user)
        self.user_token = str(refresh.access_token)

    def test_retrieve_self(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        url = reverse('users-retrieve-self')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.user.id))
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertNotIn('password', response.data)

    def test_retrieve_self_unauthorized(self):
        url = reverse('users-retrieve-self')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_public(self):
        # List endpoint should be public according to the permissions
        url = reverse('users-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) >= 1)