import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from users.models import User


class UserObjectsTestCase(TestCase):

    def test_create_user_object(self):
        user_data = {
            'password': 'user',
            'username': 'user',
            'first_name': 'name',
            'last_name': 'surname',
            'email': 'user@user.com'
        }

        user = User.objects.create(**user_data)
        auth_user = authenticate(username=user_data['username'], password=user_data['password'])
        
        {
            'id': 1, 
            'password': 'pbkdf2_sha256$1000000$BDMgN5sYDl33viZ7sqBQGE$Obije75nTkF3GPfYocahK4ak6Sg131NVVoxUr5RD6Uw=', 
            'last_login': None, 
            'is_superuser': False, 
            'username': 'user', 
            'first_name': 'name', 
            'last_name': 'surname', 
            'email': 'user@user.com', 
            'is_staff': False, 
            'is_active': True,
        }
        
        self.assertEqual(user, auth_user)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.last_login, None)
        self.assertEqual(user.last_name, user_data['last_name'])
        self.assertEqual(user.username, user_data['username'])
        self.assertEqual(user.first_name, user_data['first_name'])        
        self.assertEqual(user.email, user_data['email'])
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_active, True)


class UserObjectsListTestCase(TestCase):
    fixtures = ['users']

    def test_fixtures_loading(self):
        users = User.objects.all()
        self.assertEqual(len(users), 20)