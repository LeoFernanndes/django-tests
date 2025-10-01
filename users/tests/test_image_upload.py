from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from files.models import File


class UserImageUploadTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.upload_url = reverse('generate-upload-profile-image-presigned-url')

    @patch('django.conf.settings.S3_CLIENT.generate_presigned_url')
    def test_generate_upload_url_success(self, mock_presigned_url):
        mock_presigned_url.return_value = 'https://test-bucket.s3.amazonaws.com/presigned-url'

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        data = {
            'filename': 'profile.jpg',
            'content_type': 'image/jpeg'
        }

        response = self.client.post(self.upload_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('url', response.data)
        self.assertIn('file_id', response.data)
        self.assertEqual(response.data['url'], 'https://test-bucket.s3.amazonaws.com/presigned-url')

        # Verify File object was created
        file_id = response.data['file_id']
        file_obj = File.objects.get(id=file_id)
        self.assertEqual(file_obj.filename, 'profile.jpg')
        self.assertEqual(file_obj.filetype, 'image')
        self.assertEqual(file_obj.location, f'{self.user.id}/profile.jpg')

        # Verify the presigned URL function was called with correct parameters
        mock_presigned_url.assert_called_once()
        call_args = mock_presigned_url.call_args
        self.assertIn('Params', call_args[1])
        self.assertEqual(call_args[1]['Params']['ContentType'], 'image/jpeg')

    def test_generate_upload_url_unauthorized(self):
        data = {
            'filename': 'profile.jpg',
            'content_type': 'image/jpeg'
        }

        response = self.client.post(self.upload_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_generate_upload_url_missing_filename(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        data = {
            'content_type': 'image/jpeg'
        }

        response = self.client.post(self.upload_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('filename', response.data)

    def test_generate_upload_url_missing_content_type(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        data = {
            'filename': 'profile.jpg'
        }

        response = self.client.post(self.upload_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content_type', response.data)

    @patch('django.conf.settings.S3_CLIENT.generate_presigned_url')
    def test_generate_upload_url_different_file_types(self, mock_presigned_url):
        mock_presigned_url.return_value = 'https://test-bucket.s3.amazonaws.com/presigned-url'

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        test_files = [
            ('avatar.png', 'image/png'),
            ('profile.gif', 'image/gif'),
            ('picture.webp', 'image/webp'),
        ]

        for filename, content_type in test_files:
            with self.subTest(filename=filename, content_type=content_type):
                data = {
                    'filename': filename,
                    'content_type': content_type
                }

                response = self.client.post(self.upload_url, data)

                self.assertEqual(response.status_code, status.HTTP_200_OK)

                # Verify File object was created with correct filename
                file_id = response.data['file_id']
                file_obj = File.objects.get(id=file_id)
                self.assertEqual(file_obj.filename, filename)
                self.assertEqual(file_obj.location, f'{self.user.id}/{filename}')

    @patch('django.conf.settings.S3_CLIENT.generate_presigned_url')
    def test_file_location_includes_user_id(self, mock_presigned_url):
        mock_presigned_url.return_value = 'https://test-bucket.s3.amazonaws.com/presigned-url'

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        data = {
            'filename': 'test-image.jpg',
            'content_type': 'image/jpeg'
        }

        response = self.client.post(self.upload_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the file location includes the user ID
        file_id = response.data['file_id']
        file_obj = File.objects.get(id=file_id)
        expected_location = f'{self.user.id}/test-image.jpg'
        self.assertEqual(file_obj.location, expected_location)

        # Verify generate_presigned_url was called with the correct location
        mock_presigned_url.assert_called_once()
        call_args = mock_presigned_url.call_args
        self.assertEqual(call_args[1]['Params']['Key'], expected_location)

    @patch('django.conf.settings.S3_CLIENT.generate_presigned_url')
    def test_presigned_url_failure_handling(self, mock_presigned_url):
        # Mock the S3 client to return None (simulating an error)
        mock_presigned_url.return_value = None

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        data = {
            'filename': 'test.jpg',
            'content_type': 'image/jpeg'
        }

        response = self.client.post(self.upload_url, data)

        # The view should still return 200 but with url: None
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['url'])
        self.assertIn('file_id', response.data)

    @patch('django.conf.settings.S3_CLIENT.generate_presigned_url')
    def test_multiple_users_different_locations(self, mock_presigned_url):
        mock_presigned_url.return_value = 'https://test-bucket.s3.amazonaws.com/presigned-url'

        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )

        other_refresh = RefreshToken.for_user(other_user)
        other_token = str(other_refresh.access_token)

        # Test file upload for first user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            'filename': 'user1.jpg',
            'content_type': 'image/jpeg'
        }
        response1 = self.client.post(self.upload_url, data)

        # Test file upload for second user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token}')
        data = {
            'filename': 'user2.jpg',
            'content_type': 'image/jpeg'
        }
        response2 = self.client.post(self.upload_url, data)

        # Both should succeed
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Verify different file locations
        file1 = File.objects.get(id=response1.data['file_id'])
        file2 = File.objects.get(id=response2.data['file_id'])

        self.assertEqual(file1.location, f'{self.user.id}/user1.jpg')
        self.assertEqual(file2.location, f'{other_user.id}/user2.jpg')
        self.assertNotEqual(file1.location, file2.location)