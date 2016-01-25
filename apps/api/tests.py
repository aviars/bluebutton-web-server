from __future__ import absolute_import
from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse

from ..test import BaseApiTest


class TestApi(BaseApiTest):
    """
    Tests for the api endpoints.
    """

    def test_api_read_get_fails_without_credentials(self):
        """
        Tests that GET requests to api_read endpoint fail without
        a valid access_token.
        """
        response = self.client.get(reverse('api_read'))
        self.assertEqual(response.status_code, 403)

    def test_api_read_get(self):
        """
        Tests that api_read returns proper response.
        """
        # Create the user to obtain the token
        user = self._create_user('john', '123456')
        access_token = self._get_access_token('john', '123456')
        # Authenticate the request with the bearer access token
        auth_headers = {'HTTP_AUTHORIZATION': 'Bearer %s' % access_token}
        response = self.client.get(reverse('api_read'), **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'hello': 'World', 'oauth2': True})

    def test_api_write_get_fails_without_credentials(self):
        """
        Tests that GET requests to api_write endpoint fail without
        a valid access_token.
        """
        response = self.client.get(reverse('api_write'))
        self.assertEqual(response.status_code, 403)

    def test_api_write_post_fails_without_credentials(self):
        """
        Tests that POST requests to api_write endpoint fail without
        a valid access_token.
        """
        response = self.client.post(reverse('api_write'), data={'test': 'data'})
        self.assertEqual(response.status_code, 403)

    def test_api_write_post(self):
        """
        Tests that api_write returns proper response.
        """
        # Create the user to obtain the token
        user = self._create_user('john', '123456')
        access_token = self._get_access_token('john', '123456')
        # Prepare data for post request
        data = json.dumps({'test': 'data'})
        # Authenticate the request with the bearer access token
        auth_headers = {'HTTP_AUTHORIZATION': 'Bearer %s' % access_token}
        response = self.client.post(reverse('api_write'), data=data, content_type='application/json', **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'test': 'data', 'write': True})
