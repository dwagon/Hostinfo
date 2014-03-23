# hostinfo forms
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2008 Dougal Scott
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from .models import Host

################################################################################
################################################################################
################################################################################
class existingHostField(forms.CharField):
    """ A field for a host that is meant to already exist
    """
    def clean(self, value):
    	if not value:
	    raise forms.ValidationError("Supply a valid host name")
	try:
	    hostobj=Host.objects.get(hostname=value)
	except ObjectDoesNotExist:
	    raise forms.ValidationError("Host doesn't exist with name %s" % value)
	return hostobj

################################################################################
################################################################################
################################################################################
class newHostField(forms.CharField):
    """ A field for a host that should not already exist
    """
    def clean(self, value):
    	if not value:
	    raise forms.ValidationError("Supply a valid host name")
	try:
	    hostobj=Host.objects.get(hostname=value)
	except ObjectDoesNotExist:
	    pass
	else:
	    raise forms.ValidationError("Host already exists with name %s" % value)
	return value

################################################################################
class hostMergeForm(forms.Form):
    srchost=existingHostField()
    dsthost=existingHostField()

################################################################################
class hostRenameForm(forms.Form):
    srchost=existingHostField()
    dsthost=newHostField()

################################################################################
class hostCreateForm(forms.Form):
    newhost=newHostField()

################################################################################
class hostEditForm(forms.Form):
    hostname=existingHostField()

################################################################################
class XimportUploadForm(forms.Form):
    file=forms.FileField()

#EOF
