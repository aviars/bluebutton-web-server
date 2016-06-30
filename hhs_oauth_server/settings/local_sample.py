#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

from .base import *

print(base.ADMINS)
DEBUG = True

SECRET_KEY = "BBOAUTH2-LOCAL-_CHANGE_THIS_FAKE_KEY_TO_YOUR_OWN_SECRET_KEY"

# define app managers
ADMINS = (
    ('Alan', 'alan@example.com'),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = ['*']

AWS_ACCESS_KEY_ID = 'ADD_YOUR_AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'ADD_YOUR_AWS_SECRET_ACCESS_KEY'