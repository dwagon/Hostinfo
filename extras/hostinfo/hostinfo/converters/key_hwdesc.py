import sys
sys.path.append('/app/interactive/lib/python/site-packages')
import hardware

aka=['hwdesc', 'hardware', 'hardware platform', 'server type', 'model']

def convert(str):
    """ Keep the hardware description, but have the side effect of generating
    strings for hardware and type
    """
    if str and 'virtual' in str:
	return { 'type': 'virtual', 'vmtype': 'vmware' }
    if str==None or str=='none' or str=='???':
	return {}
    try:
	hwtype,hwname=hardware.getHardware(str)
    except hardware.UnknownHardware:
	Warning("Unknown hardware: %s" % str.lower())
	return {}
    d={}
    if hwname!='unknown':
	d['hardware']=hwname
    if hwtype!='unknown':
	d['type']=hwtype
    d['hwdesc']=str.replace(' ','_')
    return d

#EOF
