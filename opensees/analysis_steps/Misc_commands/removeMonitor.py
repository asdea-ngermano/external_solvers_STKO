import PyMpc.Units as u
import PyMpc.App
from PyMpc import *
from mpc_utils_html import *
import opensees.utils.tcl_input as tclin

def makeXObjectMetaData():
	
	# remove monitor
	at_removeMonitor = MpcAttributeMetaData()
	at_removeMonitor.type = MpcAttributeType.Index
	at_removeMonitor.name = 'remove monitor'
	at_removeMonitor.group = 'Group'
	at_removeMonitor.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('load')+'<br/>') + 
		html_par('command to remove monitor')+
		html_par(html_href('','')+'<br/>') +
		html_end()
		)
	at_removeMonitor.indexSource.type = MpcAttributeIndexSourceType.AnalysisStep
	at_removeMonitor.indexSource.addAllowedNamespace("Misc_commands")
	at_removeMonitor.indexSource.addAllowedClassList(["monitor"])
	
	xom = MpcXObjectMetaData()
	xom.name = 'removeMonitor'
	xom.addAttribute(at_removeMonitor)
	
	
	return xom

def writeTcl(pinfo):
	'''
		TODO: controllare se esiste il monitor id nella lista
	'''
	
	# remove monitor
	xobj = pinfo.analysis_step.XObject
	
	ClassName = xobj.name
	if pinfo.currentDescription != ClassName:
		pinfo.out_file.write('\n{}# {} {}'.format(pinfo.indent, xobj.Xnamespace, ClassName))
		pinfo.currentDescription = ClassName
	
	removeMonitor_at = xobj.getAttribute('remove monitor')
	if(removeMonitor_at is None):
		raise Exception('Error: cannot find "remove monitor" attribute')
	removeMonitor = removeMonitor_at.index
	
	# now write the string into the file
	pinfo.out_file.write('\n{}# we find the id in $all_monitor_actors\n'.format(pinfo.indent))
	pinfo.out_file.write('{}set id_to_remove [lsearch $all_monitor_actors "MonitorActor{}"]\n'.format(pinfo.indent, removeMonitor))
	pinfo.out_file.write('\n{}# we delete the item from the list\n'.format(pinfo.indent))
	pinfo.out_file.write('{}set all_monitor_actors [lreplace $all_monitor_actors $id_to_remove $id_to_remove]\n'.format(pinfo.indent))
	