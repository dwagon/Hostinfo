#!/usr/bin/env python
# 
# Backend module to authenticate Django via ldap
# Code heavily influenced by http://www.carthage.edu/webdev/?p=12
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# With code taken from www.carthage.edu/webdev/?p=12
# $Id: ldapBackend.py 6 2010-01-12 07:41:47Z dwagon $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/hostinfo/backends/ldapBackend.py $

import sys
sys.path.insert(0,'/app/hostinfo/lib/python/site-packages')
import ldap
from django.contrib.auth.models import User
from django.conf import settings

class LDAPBackend:
    def authenticate(self, username=None, password=None):
    	base="o=users"
	scope=ldap.SCOPE_SUBTREE
	filter="(&(objectclass=person) (uid=%s))" % username
	ret=['dn']

	try:
	    l=ldap.open(settings.AUTH_LDAP_SERVER)
	    l.protocol_version=ldap.VERSION3
	    l.simple_bind_s(settings.AUTH_LDAP_BASE_USER, settings.AUTH_LDAP_BASE_PASS)
	except ldap.LDAPError,err:
	    return None

	result_id = l.search(base, scope, filter, ret)
	result_type, result_data=l.result(result_id, 0)

	if len(result_data)!=1:
	    return None

	l.simple_bind_s(result_data[0][0], password)

	try:
	    user=User.objects.get(username__exact=username)
	except:
	    from random import choice
	    import string
	    temp_pass=""
	    for i in range(8):
	    	temp_pass=temp_pass+choice(string.letters)
	    user=User.objects.create_user(username, username+"@sensis.com.au", temp_pass)
	    user.is_staff=False
	    user.save()
	return user

    def get_user(self, user_id):
    	try:
	    return User.objects.get(pk=user_id)
	except User.DoesNotExist:
	    return None

#EOF
