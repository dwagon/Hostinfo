aka=['operating system', 'os', 'operatingsystem', 'os version', 'o/s']

def convert(str):
    if str==None:
    	return {}
    if str=="-":
	return ""
    if str in ['solaris', 'netware', 'aix', 'linux', 'windows']:
	return str
    d={}
    if ' ' in str:
	d['os']=str.split(' ',1)[0]
	d['osrev']=str.split(' ',1)[1]
    if 'windows' in str:
	d['os']='windows'
	d['osrev']=str
    return d

#EOF
