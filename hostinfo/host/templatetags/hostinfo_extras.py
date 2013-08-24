# 
# Provide a new template to pop elements of a list
# Written by Dougal Scott <dougal.scott@gmail.com>
#
# $Id: hostinfo_extras.py 6 2010-01-12 07:41:47Z dwagon $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/hostinfo/hostinfo/templatetags/hostinfo_extras.py $
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

from django import template
register = template.Library()

@register.filter
def getnextelem(value):
    """
    Go through a list and everytime it is called return the first element or return 
    """
    if value:
    	try:
	    return value.pop(0)
	except AttributeError:
	    return ''
    else:
    	return ''

#EOF
