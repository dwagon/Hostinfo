# hostinfo views
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
# $Id: views.py 71 2011-02-12 01:01:50Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/extras/hostinfo/hostinfo/views.py $
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

import datetime
import glob
import imp
import sys
import tempfile
import time

convertersdir='/app/hostinfo/converters.d'	# Directory for dynamic key converters

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response

try:
    import xlrd
    xlrd_avail=True
except ImportError:
    xlrd_avail=False

from hostinfo.hostinfo.models import Host, KeyValue, AllowedKey
from hostinfo.hostinfo.forms import importUploadForm

_convertercache=None

################################################################################
def module_from_path(filepath):
    """ Taken from djangosnippets.org/snippets/757
    """
    dirname, filename=os.path.split(filepath)
    mod_name=filename.replace('.py', '')
    dot_py_suffix=('.py', 'U', 1)	# From imp.get_suffixes()[2]
    return imp.load_module(mod_name, open(filepath), filepath, dot_py_suffix)

################################################################################
def handle_uploaded_file(f):
    fh=tempfile.mkstemp()
    filename=fh[1]
    for chunk in f.chunks():
    	os.write(fh[0],chunk)
    os.close(fh[0])
    return filename
    
################################################################################
def doImport(request):
    """ Import an XLS file 
    """
    d={
	'user': request.user,
	}
    if request.method=='POST':
    	form=importUploadForm(request.POST, request.FILES)
	if form.is_valid():
	    d['filename']=handle_uploaded_file(request.FILES['file'])
	    try:
		book=xlrd.open_workbook(d['filename'])
	    except xlrd.XLRDError, err:
	    	d['error']=err
		d['form']=importUploadForm()
		return render_to_response('import.template',d)
	    sheets=book.sheets()
	    if len(sheets)>1:
		d['sheets']=sheets
	    	return render_to_response('import_sheetselection.template', d)
	    else:
	    	d['sheetnum']=0
	    	return doHeaderSelection(request, d['filename'], book, 0)
    else:
	d['form']=importUploadForm()
    return render_to_response('import.template',d)

################################################################################
def import_makeChanges(request):
    d={}
    starttime=time.time()
    d['request']=request
    d['changes']=[]
    for ch in sorted(request.POST.keys()):
    	h,k,v=request.POST[ch].split('___')
	if k=='None' and v=='None':
	    change="Create host %s" % h
	else:
	    change="Setting %s:%s to %s" % (h, k, v)
	try:
	    status=makeChange(request, h,k,v)
	except Exception, err:
	    status="Failed: %s" % str(err)
	d['changes'].append((change, status))
    d['elapsed']=time.time()-starttime
    return render_to_response('import_results.template',d)

################################################################################
def makeChange(request, hostname, key, val):
    if key=='None' and val=='None':
	nh=Host(hostname=hostname)
	nh.origin="web import"
	nh.save(request.user)
	return "Host %s created" % hostname
    hostobj=Host.objects.get(hostname=hostname)
    keyobj=AllowedKey.objects.get(key=key)
    try:
	kv=KeyValue.objects.get(keyid=keyobj, hostid=hostobj)
	result="Updated"
    except ObjectDoesNotExist:
	kv=KeyValue(hostid=hostobj, keyid=keyobj)
	result="Set"

    kv.value=val
    kv.origin='web import'
    kv.save(request.user)
    return result

################################################################################
def import_sheetChosen(request):
    d={
    	'user': request.user,
	'request': request,
	'filename': request.POST['filename'],
	'sheet': int(request.POST['sheet']),
	}
    book=xlrd.open_workbook(d['filename'])
    return doHeaderSelection(request, d['filename'], book, d['sheet'])

################################################################################
def loadConverters():
    global _convertercache
    if _convertercache:
    	return _convertercache
    converters={}
    for fname in glob.glob(os.path.join(convertersdir, 'key_*.py')):
	repmodule=module_from_path(fname)
	keyname=os.path.split(fname)[1].replace('.py','').replace('key_','')
	converters[keyname]={'aka': repmodule.aka, 'convert': repmodule.convert}
    _convertercache=converters
    return converters

################################################################################
def matchHeader(header):
    converters=loadConverters()
    for key in converters:
    	if not hasattr(header, 'lower'):	# Can't be a good header
	    continue
    	if header.lower() in converters[key]['aka']:
	    return key.replace('key_','')
    return 'unknown'

################################################################################
def runConverter(key, value):
    converters=loadConverters()
    d={}
    try:
    	handlerfn=converters[key]['convert']
    	try:
	    results=handlerfn(value)
	except Exception,err:
	    sys.stderr.write("Failed to run converter: %s\n" % str(err))
	    return ('error', "Failed to run converter for %s: %s" % (key, str(err)))
	if type(results)==type({}):
	    d.update(results)
	elif type(results)==type(''):
	    d[key]=results.lower()
	elif type(results)==type(None):
	    pass
	elif type(results)==type(u''):
	    d[key]=results.encode('utf-8')
	else:
	    Fatal("handler %s returned %s %s" % (handlerfn, type(results), results))
    except KeyError:
	d[key]=value
    ans=[]
    for k,v in d.items():
	ans.append((k,v))
    return ans

################################################################################
def import_columnChosen(request):
    d={'request': request}
    book=xlrd.open_workbook(request.POST['filename'])
    sheet=book.sheets()[int(request.POST['sheetnum'])]
    headerrow=int(request.POST['headerrow'])
    mapping={}
    for k in request.POST.keys():
    	if not k.startswith('col_'):
	    continue
	col=int(k.replace('col_',''))
	mapping[col]=request.POST[k]

    commands=[]
    for rownum in range(headerrow+1, sheet.nrows):
    	tmp=[]
	hostname=None
    	for col, cell in enumerate(sheet.row(rownum)):
	    cellval=cellConvert(cell)
	    if mapping[col]=='ignore':
		continue
	    if mapping[col]=='hostname':
	    	hostname=runConverter('hostname', cellval)[0][1]
		continue
	    tmp.extend(runConverter(mapping[col], cellval))
	try:
	    hostobj=Host.objects.get(hostname=hostname)
	except ObjectDoesNotExist:
	    commands.append(('new host', hostname,None,None,None))
	    hostobj=None
	for k,v in tmp:
	    commands.append(update(hostname, k, v, hostobj))
    # Commands: command, hostname, key, value, olvalue
    d['commands']=commands
    return render_to_response('import_commandoutput.template', d)

################################################################################
def update(host, key, value, hostobj):
    if not hasattr(value, 'lower'):
    	value=str(value)
    value=value.lower()
    keyobj=AllowedKey.objects.get(key=key)
    if hostobj:
    	try:
	    keyval=KeyValue.objects.get(keyid=keyobj, hostid=hostobj)
	except ObjectDoesNotExist:
	    pass
	else:
	    return ('update value', host, keyobj.key, value, keyval.value)
    return ('new value', host, keyobj.key, value, None)

################################################################################
def import_headerChosen(request):
    row=int(request.POST['headerrow'][0])
    d={'request': request, 'row': row}
    keylist=[k.key for k in AllowedKey.objects.all() ]
    keylist.insert(0,'hostname')
    book=xlrd.open_workbook(request.POST['filename'])
    sheet=book.sheets()[int(request.POST['sheetnum'])]
    headers=sheet.row(row)
    tmp=[]
    for order, header in enumerate(headers):
    	h=cellConvert(header)
    	tmp.append((order, h, matchHeader(h)))
    d['headers']=tmp
    d['keylist']=keylist
    d['filename']=request.POST['filename']
    d['sheetnum']=request.POST['sheetnum']
    d['headerrow']=row
    return render_to_response('import_columnselection.template', d)

################################################################################
def doHeaderSelection(request, filename, book, sheetnum):
    d={}
    datemode=book.datemode
    sheet=book.sheets()[sheetnum]
    rows=[]
    for rownum in range(0, min(sheet.nrows, 10)):
    	tmp=[]
    	for cell in sheet.row(rownum):
	    tmp.append(cellConvert(cell, datemode))
	rows.append(tmp[:])
    d['rows']=rows
    d['filename']=filename
    d['sheetnum']=sheetnum
    return render_to_response('import_headerselection.template', d)

################################################################################
def cellConvert(cell, datemode=None):
    ctype=cell.ctype
    if ctype==0:	# Empty
	data=None
    elif ctype==1:	# TEXT
	data=cell.value.strip()
    elif ctype==2:	# NUMBER
	data=cell.value
    elif ctype==3:	# DATE
	d=xlrd.xldate_as_tuple(cell.value, datemode)
	data=datetime.date(d[0], d[1], d[2])
    elif ctype==4:	# BOOLEAN
	if cell.value==1:
	    data=True
	else:
	    data=False
    elif ctype==5:	# ERROR
	data=cell.value
    elif ctype==6:	# BLANK
	data=cell.value
    else:
	data=cell.value
	Warning("Unhandled ctype %s for value %s" % (ctype, data))
    return data

#EOF
