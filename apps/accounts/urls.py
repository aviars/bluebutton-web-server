#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from .views.core import (simple_login, create, account_settings, reissue_api_keys,
                         request_invite, mylogout, forgot_password,
                         reset_password, signup_verify, display_api_keys)

urlpatterns = [
   
    #login and Logout ------------------------------------
    url(r'login', simple_login,  name="login"),
    url(r'logout$', mylogout, name='mylogout'),
    
    #create and update account info -----------------------
    url(r'create', create,  name="accounts_create"),
    url(r'settings$', account_settings, name='account_settings'),
    
    #Request an invite to signup ---------------------------
    url(r'request-invite', request_invite,
        name="request_invite"),
    #Forgot password? ---------------------------------------
    url(r'forgot-password$', forgot_password,
        name='forgot_password'),

    #Change password using reset token ------------------------
    url(r'reset-password/(?P<reset_password_key>[^/]+)/', reset_password,
        name='reset_password'),

    #Verify th account
    url(r'signup-verify/(?P<signup_key>[^/]+)/', signup_verify,
        name='signup_verify'),
    
    url(r'display-api-keys$', display_api_keys,
        name='display_api_keys'),

    url(r'reissue-api-keys$', reissue_api_keys,
        name='reissue_api_keys'),
]
