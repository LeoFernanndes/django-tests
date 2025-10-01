import datetime
import uuid

from uuid import UUID

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import test

from organizations_management.models import Organization
from organizations_management.v1.views import OrganizationViewSet
from users.models import User


class OrganizationObjectsTestCase(TestCase):
    fixtures = ['users', 'organizations']

    def test_fixtures_loading(self):
        users = User.objects.all()
        organizations = Organization.objects.all()        
        self.assertEqual(users.count(), 149)
        self.assertEqual(organizations.count(), 3)

    def test_list_organizations_with_anonnymous_user_return_empty_set(self):
        url = reverse('organizations-list')
        response = self.client.get(url)
        self.assertEqual(response.data, {
            "detail": "Authentication credentials were not provided."
        })
        self.assertEqual(response.status_code, 401)

    def test_list_organizations_with_staff_user_return_all(self):
        url = reverse('organizations-list')
        user = User.objects.get(username='admin')
        request = test.APIRequestFactory().get(url)
        test.force_authenticate(request, user)
        response = OrganizationViewSet.as_view({'get': 'list'})(request)
            
        expected_response_data = [
            {'id': '760ff2f6-2691-4183-aae4-68c82f151c57', 'name': 'string1', 'created_at': '2025-08-23T22:58:48.781000Z', 'updated_at': '2025-08-24T00:26:27.397000Z', 'owner': UUID('05bad384-852c-430b-8e73-a68d5822dd9c'), 'admins': [], 'members': []}, 
            {'id': 'e24f3b51-b037-49cd-b91e-04401b39434e', 'name': 'string2', 'created_at': '2025-08-23T23:05:48.485000Z', 'updated_at': '2025-08-23T23:05:48.485000Z', 'owner': UUID('05bad384-852c-430b-8e73-a68d5822dd9c'), 'admins': [], 'members': []},
            {'id': '07857395-3c68-4e16-aaae-c45e3c9d1b7d', 'name': 'string3', 'created_at': '2025-08-23T23:04:28.449000Z', 'updated_at': '2025-08-23T23:04:28.449000Z', 'owner': UUID('0b6751d3-0e20-49fb-81b0-bf7f4f6d84bb'), 'admins': [], 'members': []}
        ]
        
        self.assertEqual(response.data, expected_response_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.user, user)
